import logging
import sys
from pathlib import Path

logger = logging.getLogger("uvicorn")


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent.parent.parent


def data_dir() -> Path:
    return app_dir() / "data"


def resources_dir() -> Path:
    return app_dir() / "resources"
