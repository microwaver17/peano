import gzip
import io
import pickle
from typing import Any
from zstd import ZSTD_uncompress, ZSTD_compress
from torch import Tensor
import torch


class ObjectSerializer:
    def __init__(self, value: Any):
        self.value = value

    def to_bytes(self) -> "SerializedObject":
        return SerializedObject(pickle.dumps(self.value))


class TensorSerializer:
    def __init__(self, value: Tensor):
        self.value = value

    def to_bytes(self) -> "SerializedTensor":
        bio_t = io.BytesIO()
        torch.save(self.value, bio_t)

        return SerializedTensor(bio_t.getvalue())


class SerializedObject:
    def __init__(self, value: bytes):
        self.value = value

    def to_object(self) -> Any:
        return pickle.loads(self.value)

    def to_compressed(self) -> "CompressedObject":
        return CompressedObject(ZSTD_compress(self.value, -4))


class SerializedTensor:
    def __init__(self, value: bytes):
        self.value = value

    def to_tensor(self) -> Tensor:
        bio_b = io.BytesIO(self.value)

        return torch.load(bio_b)


class CompressedObject:
    def __init__(self, value: bytes):
        self.value = value

    def to_uncompressed(self) -> SerializedObject:
        return SerializedObject(ZSTD_uncompress(self.value))
