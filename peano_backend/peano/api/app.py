import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from peano.db.connect import get_db
from peano.api import app_offload, workspace, image, command
from peano.common.settings import get_setting, set_setting_from_env
from peano.ml.recognizer import init_torch_hub

logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    image.initialize()
    init_torch_hub()
    yield


def create_app() -> FastAPI:
    set_setting_from_env()
    client = MongoClient()
    try:
        client.admin.command("ping")
    except ConnectionFailure as e:
        print(f"DBに接続できません: {e}")
        raise e

    app = FastAPI()
    app.include_router(workspace.router)
    app.include_router(image.router)
    app.include_router(command.router)
    app.include_router(app_offload.router)

    root_api = FastAPI(lifespan=lifespan)
    root_api.mount("/api", app)

    return root_api


# if __name__ == "__main__":
#     logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler()])
#     _app = create_app()
#     uvicorn.run(
#         "api.app:create_app",
#         factory=True,
#         port=PORT,
#         reload=True,
#     )
