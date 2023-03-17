from __future__ import annotations

from datetime import datetime
from typing import Optional, NewType, Type

from pydantic import BaseModel, conlist
from enum import Enum
from ulid import ULID


class StrEnum(str, Enum):
    pass


UID = NewType("UID", str)
"""UID (str)"""


def gen_ulid() -> UID:
    return str(ULID())  # type: ignore


class BaseConfig:
    validate_all = True
    validate_assignment = True


# ----- 定数 -----


class SourceType(StrEnum):
    """画像のソース"""

    file = "file"
    url = "url"


class SourceSite(StrEnum):
    """画像のソースのWebサイト"""

    pixiv = "pixiv"
    danbooru = "danbooru"
    yandere = "yandere"


# ----- メタデータ -----


class FileInfo(BaseModel):
    """ファイル情報"""

    file_size: int
    md5_hash: str

    class Config(BaseConfig):
        pass

    def __init__(self, **kwargs):
        kwargs["file_size"] = kwargs.get("file_size", -1)
        kwargs["md5_hash"] = kwargs.get("md5_hash", "")
        super().__init__(**kwargs)


class WebInfo(BaseModel):
    """取得元Webページの情報"""

    source_site: SourceSite
    id: int
    url: str
    url_parent: str

    class Config(BaseConfig):
        pass


class MLTag(BaseModel):
    name: str
    weight: float


class MLDanbooru(BaseModel):
    """機械学習(danbooru-pretrained)で得られた情報"""

    tags: list[MLTag]
    """タグと一致度"""
    feature: conlist(item_type=float, min_items=512, max_items=512)
    """特徴量 (512次元)"""

    class Config(BaseConfig):
        pass


class Metadata(BaseModel):
    """画像のメタデータ"""

    title: str
    author: str
    tags: list[str]
    description: str
    misc_info: str
    """その他の情報"""
    image_size: conlist(item_type=int, min_items=2, max_items=2)
    """(width, height)"""
    last_updated: datetime
    file_info: FileInfo
    web_info: Optional[WebInfo]
    ml: Optional[MLDanbooru]

    class Config(BaseConfig):
        pass

    def __init__(self, **kwargs):
        kwargs["title"] = kwargs.get("title", "")
        kwargs["author"] = kwargs.get("author", "")
        kwargs["tags"] = kwargs.get("tags", [])
        kwargs["description"] = kwargs.get("description", "")
        kwargs["misc_info"] = kwargs.get("misc_info", "")
        kwargs["image_size"] = kwargs.get("image_size", (-1, -1))
        kwargs["last_updated"] = kwargs.get("last_updated", datetime.now())
        kwargs["file_info"] = kwargs.get("file_info", FileInfo())
        kwargs["web_info"] = kwargs.get("web_info", None)
        kwargs["ml"] = kwargs.get("ml", None)
        super().__init__(**kwargs)


# ----- 画像 -----


class Image(BaseModel):
    """画像"""

    id: UID
    source_type: SourceType
    path: str
    """絶対ファイルパス or URL"""
    belong_workspaces: list[str]
    metadata: Metadata
    relative_image_ids: list[UID]

    class Config(BaseConfig):
        pass

    def __init__(self, **kwargs):
        kwargs["id"] = kwargs.get("id", gen_ulid())
        kwargs["metadata"] = kwargs.get("metadata", Metadata())
        kwargs["relative_image_ids"] = kwargs.get("relative_image_ids", [])
        super().__init__(**kwargs)


# ---- ワークスペース -----


class RemoteSource(BaseModel):
    """新しい画像をWebページから取得する方法"""

    name: str
    site: SourceSite
    query: str

    class Config(BaseConfig):
        pass


class Workspace(BaseModel):
    """ワークスペース"""

    name: str
    scan_directories: list[str]
    scan_remotes: dict[str, RemoteSource]
    ignore_patterns: list[str]
    """平均"""

    class Config(BaseConfig):
        pass

    def __init__(self, **kwargs):
        kwargs["image_ids"] = kwargs.get("image_ids", [])
        kwargs["scan_directories"] = kwargs.get("scan_directories", [])
        kwargs["scan_remotes"] = kwargs.get("scan_remotes", {})
        kwargs["ignore_patterns"] = kwargs.get("ignore_patterns", [])
        kwargs["mean"] = kwargs.get("mean", [0.0] * 512)

        super().__init__(**kwargs)


# ----- ユーザーデータ -----


class ActionHistory(BaseModel):
    """行動履歴"""

    image_id: UID
    last_updated: datetime
    """行動日時"""

    class Config(BaseConfig):
        pass


class SimilarSearchQuery(BaseModel):
    """類似検索クエリ"""

    name: str
    image_ids: list[UID]
    last_updated: datetime
    """最終クエリ保存日時"""

    class Config(BaseConfig):
        pass


class UserData(BaseModel):
    """ユーザーデータ"""

    view_histories: list[ActionHistory]
    similar_search_query: dict[str, SimilarSearchQuery]
    likes: list[ActionHistory]

    class Config(BaseConfig):
        pass

    def __init__(self, **kwargs):
        kwargs["view_histories"] = kwargs.get("view_histories", [])
        kwargs["similar_search_query"] = kwargs.get("similar_search_query", {})
        kwargs["likes"] = kwargs.get("likes", [])
        super().__init__(**kwargs)


class DB(BaseModel):
    """データベース"""

    class Config(BaseConfig):
        pass

    images: dict[UID, Image]
    workspaces: dict[str, Workspace]
    userdata: UserData

    def __init__(self, **kwargs):
        kwargs["images"] = kwargs.get("images", {})
        kwargs["workspaces"] = kwargs.get("workspaces", {})
        kwargs["userdata"] = kwargs.get("userdata", UserData())
        super().__init__(**kwargs)


if __name__ == "__main__":
    scheme = DB.schema_json(indent=2, ensure_ascii=False)
    print(scheme)
