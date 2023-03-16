from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import tomli
import logging
from peano.common import pathfinder

from peano.common.definitions import ScanSourceType
from peano.common.pathfinder import app_dir

_FILENAME = "settings.toml"

logger = logging.getLogger("uvicorn")


class SettingFileException(Exception):
    pass


@dataclass(frozen=True)
class ImageSource:
    """画像のソーズ"""

    name: str
    type: ScanSourceType
    path: list[Path]
    ignore_patterns: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Settings:
    image_sources: list[ImageSource]


def load_settings():
    with open(app_dir() / _FILENAME, "r", encoding="utf8") as f:
        data = tomli.loads(f.read())

    return from_dict(
        data_class=Settings,
        data=data,
        config=Config(cast=[Enum], type_hooks={Path: Path}),
    )

    # def __init__(self):
    #     self.sources: list[Source] = []
    #     self.load_settings()
    #
    # def load_settings(self):
    #     self.sources = []
    #
    #     with open(pathfinder.app_dir() / _FILENAME, "r", encoding="utf8") as f:
    #         data = tomli.loads(f.read())
    #
    #     # yamlの設定ファイルからSourceインスタンスに変換
    #     toml_source = data["source"]
    #     if not isinstance(toml_source, list):
    #         raise SettingFileException(f"設定ファイルのルートがリスト形式になっていません")
    #     for src in toml_source:
    #         for k in ("name", "type", "path"):
    #             if k not in src:
    #                 raise SettingFileException(f"nameがありません {src}")
    #
    #         name = src["name"]
    #         path = [Path(p) for p in src["path"]]
    #
    #         if src["type"] not in list(ScanSourceType):
    #             raise SettingFileException(f"{name}のtypeが正しくありません ({src['type']})")
    #         type = src["type"]
    #
    #         ignore_patterns = src.get("ignore_patterns", [])
    #         for ptn in ignore_patterns:
    #             if not isinstance(ptn, str):
    #                 raise SettingFileException(f"{name}のpatternが正しくありません ({ptn})")
    #
    #         source = Source(
    #             name=name, type=type, path=path, ignore_patterns=ignore_patterns
    #         )
    #         self.sources.append(source)
    #         logger.info(f"設定追加 {source}")
