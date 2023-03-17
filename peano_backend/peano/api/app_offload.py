from collections import namedtuple
from concurrent import futures
from dataclasses import dataclass

from fastapi import APIRouter, Body, FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
from torch import Tensor
import torch
from peano.common.definitions import TAG_MAX_SIZE, TAG_THRESH
from peano.common.pathfinder import data_dir
from peano.common.serialize import CompressedObject, SerializedTensor, ObjectSerializer
from peano.common.settings import get_setting, set_setting_from_env
from peano.db.models import MLDanbooru, MLTag

from peano.ml.recognizer import get_recognizer

router = APIRouter(prefix="/offload", tags=["offload"])

_executor = None


def get_executor():
    global _executor

    if _executor is None:
        print("プロセスプール作成")
        setting = get_setting()
        _executor = futures.ProcessPoolExecutor(max_workers=setting.proc_num)

    return _executor


def create_app() -> FastAPI:
    set_setting_from_env()
    print(get_setting())

    app = FastAPI(lifespan=lifespan)
    app.include_router(router)

    root_api = FastAPI()
    root_api.mount("/api", app)

    return root_api


def lifespan(app: FastAPI):
    yield
    print("プロセスプール終了")
    get_executor().shutdown()


class OffloadResponse(BaseModel):
    image_id: str
    tags: list[MLTag]
    feature: list[float]


class OffloadRequest(BaseModel):
    image_id: str
    batch_bytes: bytes


@dataclass
class JobHistory:
    image_id: str
    job: futures.Future[tuple[dict[str, float], list[float]]]


@router.post("/recognize")
def recognize_tensor(offload_request_data: bytes = Body()) -> Response:
    recog = get_recognizer()
    setting = get_setting()
    req: list[OffloadRequest] = (
        CompressedObject(offload_request_data).to_uncompressed().to_object()
    )

    res_off: list[OffloadResponse] = []
    if torch.cuda.is_available():
        # GPU使用
        for r in req:
            batch = SerializedTensor(r.batch_bytes).to_tensor()
            tags, feature = recog.recognize_batch(
                batch, tag_thresh=TAG_THRESH, tag_max_size=TAG_MAX_SIZE
            )
            tags_ml = [MLTag(name=name, weight=weight) for name, weight in tags.items()]
            res_off.append(
                OffloadResponse(image_id=r.image_id, tags=tags_ml, feature=feature)
            )

    else:
        # CPUで並列実行
        job_hist: list[JobHistory] = []
        executor = get_executor()
        for r in req:
            batch = SerializedTensor(r.batch_bytes).to_tensor()
            job_hist.append(
                JobHistory(
                    image_id=r.image_id,
                    job=executor.submit(
                        recog.recognize_batch,
                        batch,
                        tag_thresh=TAG_THRESH,
                        tag_max_size=TAG_MAX_SIZE,
                    ),
                )
            )
        for jh in job_hist:
            tags, feature = jh.job.result()
            tags_ml = [MLTag(name=name, weight=weight) for name, weight in tags.items()]
            res_off.append(
                OffloadResponse(image_id=jh.image_id, tags=tags_ml, feature=feature)
            )
    res = ObjectSerializer(res_off).to_bytes().to_compressed().value
    # print(f"batch size: {len(batch_b_gz)}")
    # print(f"ml size: {len(ml_pkl)}")

    return Response(content=res, media_type="application/octet-stream")
