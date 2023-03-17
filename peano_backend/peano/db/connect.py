from __future__ import annotations

import logging

from pymongo import MongoClient
from pymongo.collection import Collection

logger = logging.getLogger("uvicorn")


class _DB:
    """DB(dict)の排他制御を行う"""

    def __init__(self):
        self._client = MongoClient()
        self._db = self._client["peano"]

    @property
    def db(self):
        return self._db

    @property
    def images(self) -> Collection:
        return self._db["images"]

    @property
    def workspaces(self):
        return self._db["workspaces"]

    @property
    def setting(self):
        return self._db["setting"]

    @property
    def userdata(self):
        return self._db["userdata"]


def get_db():
    db = _DB()
    return db


def fix_db():
    """
    DBの整合性をチェック
    """
    print("DB整合性チェック開始")
    db = get_db()
    # with get_db as db:
    #     # workspaceに設定されている画像がimagesに存在しない場合、workspaceから削除
    #     for workspace in db.workspaces.values():
    #         for img_id in workspace.image_ids:
    #             if img_id not in db.images:
    #                 print(img_id)
    #                 workspace.image_ids = [
    #                     imid for imid in workspace.image_ids if imid != img_id
    #                 ]
    print("imageに設定されているワークスペースの重複削除")

    print("インデックス作成")
    db.images.create_index([("id", 1)])
    db.images.create_index([("path", 1)])
    db.images.create_index([("belong_workspaces", 1)])

    print("重複してワークスペースが設定されているimageを修正")
    dup_ws_images_db = db.images.aggregate(
        [
            {
                "$group": {
                    "_id": "$belong_workspaces",
                    "ids": {"$push": "$id"},
                    "count": {"$sum": 1},
                }
            },
            {"$match": {"count": {"$gt": 1}}},
        ]
    )
    for img_db in dup_ws_images_db:
        ids: list[str] = img_db["ids"]
        ws_names: list[str] = list(set(img_db["_id"]))
        print(ws_names)
        print(f"{' '.join(ws_names)} {img_db['count']} {ids[0]} ...")
        db.images.update_many(
            {"id": {"$in": ids}}, {"$set": {"belong_workspaces": ws_names}}
        )

    # print("ワークスペースが設定されていない画像を削除")

    # res = db.images.delete_many({"belong_workspaces": []})
    # print(f"{res.deleted_count}件")

    print("DB整合性チェック終了")
