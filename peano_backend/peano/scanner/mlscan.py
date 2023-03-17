from datetime import datetime
import gzip
import io
import pickle
import time
from threading import Event, Lock, Thread
from concurrent import futures
from typing import Optional

import numpy as np
import requests
import torch
from peano.api.app_offload import OffloadRequest, OffloadResponse
from peano.common.definitions import (
    TAG_MAX_SIZE,
    TAG_THRESH,
)
from peano.common.pathfinder import data_dir
from peano.common.serialize import TensorSerializer, ObjectSerializer, CompressedObject
from peano.common.settings import get_setting

from peano.db.connect import get_db
from peano.db.models import MLDanbooru, Image, MLTag
from peano.loader import loader
from peano.ml.recognizer import get_recognizer

exit_event = Event()
re_entry_lock = Lock()


def _recog_one(img: Image) -> tuple[MLDanbooru, str]:
    recognizer = get_recognizer()
    img_b = loader.get_loader(img).load()
    tags, feature = recognizer.recognize(
        img_b=img_b, tag_thresh=TAG_THRESH, tag_max_size=TAG_MAX_SIZE
    )
    ml_tags = [MLTag(name=name, weight=weight) for name, weight in tags.items()]
    ml = MLDanbooru(tags=ml_tags, feature=feature)

    return ml, img.id


def _recog_one_offload_make_batches_bytes(imgs: list[Image]) -> bytes:
    """
    外部に投げる
    """
    recognizer = get_recognizer()

    req_batches: list[OffloadRequest] = []
    for img in imgs:
        img_b = loader.get_loader(img).load()
        batch = recognizer.recognize_make_batch(img_b)
        req_batches.append(
            OffloadRequest(
                image_id=img.id, batch_bytes=TensorSerializer(batch).to_bytes().value
            )
        )
    req_batches_bytes = ObjectSerializer(req_batches).to_bytes().to_compressed().value

    (data_dir() / "test_res.bin").write_bytes(
        ObjectSerializer(ObjectSerializer(req_batches).to_bytes().value)
        .to_bytes()
        .value
    )
    (data_dir() / "test_res.bin.zstd").write_bytes(req_batches_bytes)

    return req_batches_bytes


def _recog_one_offload_request(
    req_batches_bytes: bytes,
) -> list[tuple[MLDanbooru, str]]:
    setting = get_setting()

    res = requests.post(
        setting.offload_url + "/api/offload/recognize",
        data=req_batches_bytes,
        headers={"Content-Type": "application/octet-stream"},
    )
    if res.status_code != 200:
        raise Exception(f"リクエストエラー{res.status_code}: {res.text}")

    res_off: list[OffloadResponse] = (
        CompressedObject(res.content).to_uncompressed().to_object()
    )
    res_ml: list[tuple[MLDanbooru, str]] = []
    for ro in res_off:
        ml_tags = [MLTag(name=tag.name, weight=tag.weight) for tag in ro.tags]
        res_ml.append((MLDanbooru(tags=ml_tags, feature=ro.feature), ro.image_id))

    return res_ml


def scan_concurrent(ws_name: str):
    print("ML推論開始（並列）")
    db = get_db()
    setting = get_setting()

    # 画像取得
    images_db = db.images.find({"belong_workspaces": ws_name, "metadata.ml": None})
    total_count_list = list(
        db.images.aggregate(
            [
                {"$match": {"belong_workspaces": ws_name, "metadata.ml": None}},
                {"$count": "total"},
            ]
        )
    )
    if len(total_count_list) > 0:
        total_count = total_count_list[0]["total"]
    else:
        total_count = 0

    jobs: list[futures.Future[tuple[MLDanbooru, str]]] = []
    with futures.ProcessPoolExecutor(max_workers=setting.proc_num) as executor:
        for i, img_db in enumerate(images_db):
            img = Image(**img_db)

            # 外部から中断信号
            if exit_event.is_set():
                exit_event.clear()
                print("中断しました。")
                break

            # 並列プロセス実行
            jobs.append(executor.submit(_recog_one, img))

            # 一定回数ジョブを送ったら、setting.proc_numだけ結果を取得お
            if len(jobs) >= setting.proc_num * 3:
                req_jobs = jobs[: setting.proc_num]
                jobs = jobs[setting.proc_num :]

                job_wait_start_time = time.time()
                for i_job, job in enumerate(req_jobs):
                    ml, img_id = job.result()

                    # ML情報追加
                    db.images.update_one(
                        {"id": img_id}, {"$set": {"metadata.ml": ml.dict()}}
                    )
                    print(
                        f"[ML {datetime.now().isoformat()}] {(i - setting.proc_num) + i_job + 1}/{total_count}件 ...{str(img.path)[-60:]}"
                    )
                job_exec_time = (time.time() - job_wait_start_time) / setting.proc_num
                print(f"[ML] 実行時間: {job_exec_time:.3f}")

        # 実行中プロセスがあれば待って結果を受け取る
        print("残りのプロセス処理中")
        for i_job, job in enumerate(jobs):
            ml, img_id = job.result()
            print(f"[{i_job + 1}/{len(jobs)}] {img_id}")

            # ML情報追加
            db.images.update_one({"id": img_id}, {"$set": {"metadata.ml": ml.dict()}})

    print("完了")
    exit_event.clear()


def scan_offload_only(ws_name: str):
    print("ML推論開始（オフロード）")
    db = get_db()
    setting = get_setting()

    # 画像取得
    images_db = db.images.find({"belong_workspaces": ws_name, "metadata.ml": None})
    total_count_list = list(
        db.images.aggregate(
            [
                {"$match": {"belong_workspaces": ws_name, "metadata.ml": None}},
                {"$count": "total"},
            ]
        )
    )
    if len(total_count_list) > 0:
        total_count = total_count_list[0]["total"]
    else:
        total_count = 0

    image_queue: list[Image] = []
    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        next_batches_future: Optional[futures.Future] = None
        for i, img_db in enumerate(images_db):
            # 外部から中断信号
            if exit_event.is_set():
                exit_event.clear()
                print("中断しました。")
                break

            img = Image(**img_db)
            image_queue.append(img)

            # 一度に処理する量に達したらリクエスト
            if len(image_queue) >= setting.offload_queue_num * 2:
                job_start_time = time.time()
                current_image_queue = image_queue[: setting.offload_queue_num]
                next_image_queue = image_queue[setting.offload_queue_num :]

                if next_batches_future is None:
                    batches_bytes = _recog_one_offload_make_batches_bytes(
                        current_image_queue
                    )
                else:
                    batches_bytes = next_batches_future.result()

                next_batches_future = executor.submit(
                    _recog_one_offload_make_batches_bytes, next_image_queue
                )

                res_list = _recog_one_offload_request(batches_bytes)
                image_queue = []
                for r in res_list:
                    # ML情報追加
                    ml, img_id = r
                    db.images.update_one(
                        {"id": img_id}, {"$set": {"metadata.ml": ml.dict()}}
                    )
                    print(
                        f"[ML {datetime.now().isoformat()}] {i + 1}/{total_count}件 ...{str(img.path)[-60:]}"
                    )

                job_exec_time = (
                    time.time() - job_start_time
                ) / setting.offload_queue_num
                print(f"[ML] 実行時間: {job_exec_time:.3f}")

    print("完了")
    exit_event.clear()


def scan(ws_name: str):
    with re_entry_lock:
        setting = get_setting()
        if setting.offload_only is True:
            scan_offload_only(ws_name)
            return
        else:
            scan_concurrent(ws_name)
            return
