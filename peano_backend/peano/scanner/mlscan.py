from datetime import datetime
import gzip
import io
import pickle
import time
from threading import Event
from concurrent import futures

import numpy as np
import requests
import torch
from peano.common.definitions import (
    ENABLE_OFFLOAD,
    OFFLOAD_URL,
    TAG_MAX_SIZE,
    TAG_THRESH,
)
from peano.common.serialize import pickle_gz_to_object, tensor_to_gz

from peano.db.connect import get_db
from peano.db.models import MLDanbooru, Image, MLTag
from peano.loader import loader
from peano.ml.recognizer import get_recognizer

exit_event = Event()


def _recog_one(img: Image) -> tuple[MLDanbooru, str]:
    recognizer = get_recognizer()
    img_b = loader.get_loader(img).load()
    tags, feature = recognizer.recognize(
        img_b=img_b, tag_thresh=TAG_THRESH, tag_max_size=TAG_MAX_SIZE
    )
    ml_tags = [MLTag(name=name, weight=weight) for name, weight in tags.items()]
    ml = MLDanbooru(tags=ml_tags, feature=feature)

    return ml, img.id


def _recog_one_offload(img: Image) -> tuple[MLDanbooru, str]:
    """
    外部に投げる
    """
    recognizer = get_recognizer()
    img_b = loader.get_loader(img).load()

    batch = recognizer.recognize_make_batch(img_b)
    batch_gz = tensor_to_gz(batch)
    res = requests.post(
        OFFLOAD_URL + "/api/offload/recognize",
        data=batch_gz,
        headers={"Content-Type": "application/octet-stream"},
    )
    if res.status_code != 200:
        raise Exception(f"リクエストエラー{res.status_code}: {res.text}")

    tags, feature = pickle_gz_to_object(res.content)
    ml_tags = [MLTag(name=name, weight=weight) for name, weight in tags.items()]
    ml = MLDanbooru(tags=ml_tags, feature=feature)

    return ml, img.id


def scan_concurrent(ws_name: str):
    print("ML推論開始（並列）")
    db = get_db()

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
    proc_num = 2
    with futures.ProcessPoolExecutor(max_workers=proc_num) as executor:
        for i, img_db in enumerate(images_db):
            img = Image(**img_db)

            # 外部から中断信号
            if exit_event.is_set():
                exit_event.clear()
                print("中断しました。")
                break

            # 並列プロセス実行
            jobs.append(executor.submit(_recog_one, img))

            # 一定回数ジョブを送ったら、proc_numだけ結果を取得お
            if len(jobs) >= proc_num * 3:
                req_jobs = jobs[:proc_num]
                jobs = jobs[proc_num:]

                job_wait_start_time = time.time()
                for i_job, job in enumerate(req_jobs):
                    ml, img_id = job.result()

                    # ML情報追加
                    db.images.update_one(
                        {"id": img_id}, {"$set": {"metadata.ml": ml.dict()}}
                    )
                    print(
                        f"[ML {datetime.now().isoformat()}] {(i - proc_num) + i_job + 1}/{total_count}件 ...{str(img.path)[-60:]}"
                    )
                job_exec_time = (time.time() - job_wait_start_time) / proc_num
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


def scan_offload(ws_name: str):
    print("ML推論開始（オフロード）")
    db = get_db()

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

    for i, img_db in enumerate(images_db):
        # 外部から中断信号
        if exit_event.is_set():
            exit_event.clear()
            print("中断しました。")
            break

        img = Image(**img_db)
        ml, img_id = _recog_one_offload(img)

        # ML情報追加
        db.images.update_one({"id": img_id}, {"$set": {"metadata.ml": ml.dict()}})
        print(
            f"[ML {datetime.now().isoformat()}] {i + 1}/{total_count}件 ...{str(img.path)[-60:]}"
        )

    print("完了")
    exit_event.clear()


def scan(ws_name: str):
    if ENABLE_OFFLOAD is True:
        scan_offload(ws_name)
        return
    else:
        scan_concurrent(ws_name)
        return
