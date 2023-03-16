import gzip
import os
import pickle
import sys
import time
from pymongo.database import Database

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from peano.common.pathfinder import data_dir
from peano.db.models import DB

from pymongo import MongoClient

if __name__ == "__main__":
    if input("データーベースが削除されます。よろしいですか？(y/n)") != "y":
        exit()

    print("pickle読み込み")
    with gzip.open(data_dir() / "db.pickle.gz", "rb") as f:
        db_pkl: DB = pickle.load(f)
    print("pickle読み込み終了")

    client = MongoClient()
    db: Database = client.peano

    db.drop_collection("images")
    db.drop_collection("workspaces")
    db.drop_collection("userdata")

    print("images書き込み")
    last_time = time.time()
    image_insert_queue = []
    for i, image in enumerate(db_pkl.images.values()):
        image_insert_queue.append(image.dict())
        if len(image_insert_queue) > 5000:
            db["images"].insert_many(image_insert_queue)
            image_insert_queue = []

        now = time.time()
        if now - last_time > 1:
            last_time = now
            print(f"[{i + 1}/{len(db_pkl.images)}]{image.path[-100:]}")

    print("workspaces書き込み")
    for name, workspace in db_pkl.workspaces.items():
        db.workspaces.insert_one(workspace.dict())

        now = time.time()
        if now - last_time > 1:
            last_time = now
            print(f"{name}")

    print("userdata書き込み")
    db["userdata"].insert_one(db_pkl.userdata.dict())
