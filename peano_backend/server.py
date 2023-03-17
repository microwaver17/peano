import argparse
import logging
import os
from random import choice
from threading import Thread
import asyncio

import torch
import uvicorn
from uvicorn import Config, Server

from peano.api.app import create_app
from peano.common.definitions import PORT, PORT_OFFLOAD, OFFLOAD_URL_REMOTE

from peano.common.pathfinder import app_dir, resources_dir, data_dir
from peano.common.settings import get_setting, Setting
from peano.scanner import mlscan

logger = logging.getLogger("uvicorn")


def batch_mlscan(ws_name: str):
    mlscan.scan(ws_name)

    return


if __name__ == "__main__":
    if torch.cuda.is_available():
        print("GPU(CUDA)使用")
    else:
        print("CPU使用")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        nargs="?",
        type=str,
        default="server",
        choices=["server", "mlscan", "offload"],
    )
    parser.add_argument("-p", "--port", type=int, default=None)
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-pn", "--parallel-num", type=int, default=None)
    parser.add_argument("-oe", "--offload-enable", action="store_true")
    parser.add_argument("-oo", "--offload-only", action="store_true")
    parser.add_argument("-or", "--offload-remote", action="store_true")
    args = parser.parse_args()

    setting = Setting()

    port = PORT
    if args.port is not None:
        port = args.port
        print(f"[設定] ポート変更: {port}")
    if args.mode == "offload":
        port = PORT_OFFLOAD

    if args.verbose:
        print(f"[設定] 詳細表示")
        loglevel = "INFO"
    else:
        loglevel = "ERROR"

    if args.parallel_num is not None:
        print(f"[設定] 並列数 {args.parallel_num}")
        setting.proc_num = args.parallel_num

    if args.offload_enable is True:
        print(f"[設定] オフロード有効")
        setting.offload_enable = True

    if args.offload_only is True:
        print(f"[設定] オフロードのみ")
        setting.offload_only = True

    if args.mode == "mlscal":
        batch_mlscan(args.mlscan)
        exit()

    if args.mode == "server":
        app_name = "peano.api.app:create_app"
    elif args.mode == "offload":
        app_name = "peano.api.app_offload:create_app"
    else:
        print(f"不正なモード: {args.mode}")
        exit()

    if args.offload_remote is True:
        setting.offload_url = OFFLOAD_URL_REMOTE

    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["default"][
        "fmt"
    ] = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    log_config["loggers"]["uvicorn.access"]["level"] = loglevel
    log_config["loggers"]["uvicorn.error"]["level"] = loglevel

    config = Config(app_name)
    config.factory = True
    config.port = port

    if args.debug:
        print("[設定] DEBUGモード")
        config.reload = True
        config.reload_dirs = str(app_dir() / "peano")
        config.reload_excludes = [str(data_dir()), str(resources_dir())]
        config.log_config = log_config
        config.workers = 1

    else:
        config.workers = setting.proc_num

    # 設定を一旦環境変数に格納
    os.environ["default_config_json"] = setting.json()

    server = Server(config)
    server.run()
