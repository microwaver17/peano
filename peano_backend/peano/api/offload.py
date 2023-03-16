import gzip
import io
import pickle
from fastapi import APIRouter, Body
from fastapi.responses import Response
import torch
from peano.common.definitions import TAG_MAX_SIZE, TAG_THRESH
from peano.common.serialize import gz_to_tensor, object_to_pickle_gz

from peano.ml.recognizer import get_recognizer


router = APIRouter(prefix="/offload", tags=["offload"])


@router.post("/recognize")
def recognize_tensor(batch_b_gz: bytes = Body()) -> Response:
    recog = get_recognizer()
    batch = gz_to_tensor(batch_b_gz)

    ml = recog.recognize_batch(batch, tag_thresh=TAG_THRESH, tag_max_size=TAG_MAX_SIZE)

    ml_pkl = object_to_pickle_gz(ml)

    # print(f"batch size: {len(batch_b_gz)}")
    # print(f"ml size: {len(ml_pkl)}")

    return Response(content=ml_pkl, media_type="application/octet-stream")
