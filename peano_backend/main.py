import argparse
import logging
from hypercorn.asyncio import serve
from hypercorn.config import Config
import asyncio

import uvicorn
from peano.api.app import create_app

from peano.common.definitions import PORT, ENABLE_OFFLOAD
from peano.common.pathfinder import app_dir, resources_dir, data_dir

logger = logging.getLogger("uvicorn")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=None)
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-ofl", "--enable-offload", action="store_true")
    args = parser.parse_args()

    if args.port is not None:
        PORT = args.port
        print(f"[設定] ポート変更: {PORT}")

    if args.verbose:
        print(f"[設定] 詳細表示")
        loglevel = "INFO"
    else:
        loglevel = "ERROR"

    if args.enable_offload == True:
        print(f"[設定] オフロード有効")
        ENABLE_OFFLOAD = True

    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["default"][
        "fmt"
    ] = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    log_config["loggers"]["uvicorn.access"]["level"] = loglevel
    log_config["loggers"]["uvicorn.error"]["level"] = loglevel

    if args.debug:
        print("[設定] DEBUGモード")
        kwargs = {
            "reload": True,
            "reload_dirs": str(app_dir() / "peano"),
            "reload_excludes": [str(data_dir()), str(resources_dir())],
            "log_config": log_config,
        }

        uvicorn.run("peano.api.app:create_app", factory=True, port=PORT, **kwargs)

    else:
        kwargs = {}

    uvicorn.run("peano.api.app:create_app", factory=True, port=PORT, **kwargs)
