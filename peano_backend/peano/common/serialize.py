import gzip
import io
import pickle
from typing import Any

from torch import Tensor
import torch


def object_to_pickle_gz(obj: Any) -> bytes:
    bio_b_gz = io.BytesIO()
    with gzip.open(bio_b_gz, "wb", compresslevel=1) as f:
        pickle.dump(obj, f)

    return bio_b_gz.getvalue()


def pickle_gz_to_object(pkl: bytes) -> Any:
    bio_b = io.BytesIO(pkl)
    with gzip.open(bio_b, "rb") as f:
        obj = pickle.load(f)

    return obj


def tensor_to_gz(t: Tensor) -> bytes:
    bio_t_gz = io.BytesIO()
    with gzip.open(bio_t_gz, "wb", compresslevel=1) as f:
        torch.save(t, f)

    return bio_t_gz.getvalue()


def gz_to_tensor(gz: bytes) -> Tensor:
    bio_gz = io.BytesIO(gz)
    with gzip.open(bio_gz, "rb") as f:
        t = torch.load(f)

    return t
