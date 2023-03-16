from __future__ import annotations
from typing import Optional
from pydantic import BaseModel

from peano.db.models import UID


class ResultResponse(BaseModel):
    result: bool
    reason: str

    def __init__(self, **kwargs):
        kwargs["reason"] = kwargs.get("reason", "")
        super().__init__(**kwargs)


class ImageDigest(BaseModel):
    """画像"""

    id: UID
    similarity: Optional[float]

    def __init__(self, **kwargs):
        kwargs["similarity"] = kwargs.get("similarity", None)
        super().__init__(**kwargs)
