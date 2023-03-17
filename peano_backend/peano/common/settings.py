import json
import os
from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel, BaseSettings

from peano.common.definitions import OFFLOAD_URL_LOCAL
from peano.db.connect import get_db


class Setting(BaseSettings):
    offload_url: str = OFFLOAD_URL_LOCAL
    offload_enable: bool = False
    offload_only: bool = False
    proc_num: int = 2
    offload_queue_num: int = 4


_setting = Setting()


def get_setting() -> Setting:
    return _setting


def set_setting_from_env():
    global _setting

    new_js = json.loads(os.environ["default_config_json"])
    _setting = Setting(**new_js)
