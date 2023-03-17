import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from typing import Any
from peano.common.settings import Setting


from peano.db.connect import get_db


def ml_tags_dict_to_list_20230315_00():
    """MLタグをdictからリストに"""

    db = get_db()

    # Object型がなければ終了
    if db.images.find_one({"metadata.ml.tags": {"$type": 3}}) is None:
        return

    print(ml_tags_dict_to_list_20230315_00.__doc__)
    if input("実行しますか？(y/n)): ") != "y":
        return

    images_db = db.images.find({"metadata.ml.tags": {"$ne": None}})
    for img_db in images_db:
        if isinstance(img_db["metadata"]["ml"]["tags"], list):
            print(f'Skip: {img_db["id"]}')
            continue

        tags_list: list[dict[str, Any]] = []
        for tag, weight in img_db["metadata"]["ml"]["tags"].items():
            tags_list.append({"name": tag, "weight": weight})

        db.images.update_one(
            {"id": img_db["id"]}, {"$set": {"metadata.ml.tags": tags_list}}
        )

        print(f'Change: {img_db["id"]}')


def make_setting_collection_20230317_00():
    """設定情報を保存するコレクションを作成"""

    db = get_db()

    # settingがなければ終了
    if db.setting.find_one() is not None:
        return

    print(make_setting_collection_20230317_00.__doc__)
    if input("実行しますか？(y/n)): ") != "y":
        return

    setting = Setting()
    db.setting.insert_one(setting.dict())


if __name__ == "__main__":
    ml_tags_dict_to_list_20230315_00()
    make_setting_collection_20230317_00()
