import gzip
import os
import shutil
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pickle

from peano.db.models import DB, UID
from peano.common.pathfinder import data_dir


def move_image_ids_to_workspace_20230312(db: DB) -> DB:
    print("[move image_ids to workspace]")

    ws_to_images: dict[str, list[UID]] = {}
    for ws_name in db.workspaces:
        ws_to_images[ws_name] = db.workspace_image_map[ws_name]

    db = DB(**db.dict())

    for ws_name in db.workspaces:
        db.workspaces[ws_name].image_ids = ws_to_images[ws_name]

    return db


def make_ignore_images_20230311(db: DB) -> DB:
    print("[make ignore images]")
    new_ignore_ids: dict[str, list[str]] = {}

    print("既存の無視リスト取得")
    for ws_name in db.workspaces:
        ignore_images_ids = [
            img_id
            for img_id in db.workspace_image_map[ws_name]
            if db.images[img_id].ignore
        ]
        # print("\n".join(ignore_iamges_ids))
        new_ignore_ids[ws_name] = ignore_images_ids

    print("新しいDBを作成")
    db = DB(**db.dict())
    print("新しい無視リストを作成")
    for ws_name in db.workspaces:
        db.workspaces[ws_name].ignore_image_ids = new_ignore_ids[ws_name]

    return db


def move_image_ids_to_images_20230312(db: DB) -> DB:
    print("[move_image_ids_to_images]")

    print("image idを取得")
    new_image_ids = {}
    for ws_name in db.workspaces.keys():
        new_image_ids[ws_name] = db.workspaces[ws_name].image_ids

    print("新しいDBを作成")
    db = DB(**db.dict())

    print("image idを作成")
    for ws_name in new_image_ids.keys():
        for img_id in new_image_ids[ws_name]:
            db.images[img_id].belong_workspaces.append(ws_name)

    return db


def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "output_type", type=str, help="出力形式", choices=["json", "pickle", "bench"]
    # )
    # args = parser.parse_args()

    print("pickle読み込み")
    with gzip.open(data_dir() / "db.pickle.gz", "rb") as f:
        db: DB = pickle.load(f)

    is_changed = False

    ws_name = list(db.workspaces.keys())[0]
    img_id = list(db.images.keys())[0]

    # if not hasattr(db.workspaces[ws_name], "ignore_image_ids"):
    #     db = make_ignore_images_20230311(db)
    #     is_changed = True

    # if not hasattr(db.workspaces[ws_name], "workspace_image_map"):
    #     db = move_image_ids_to_workspace_20230312(db)
    #     is_changed = True

    if not hasattr(db.images[img_id], "belong_workspaces"):
        db = move_image_ids_to_images_20230312(db)
        is_changed = True

    if is_changed:
        print("バックアップ")
        shutil.copyfile(
            data_dir() / "db.pickle.gz",
            data_dir() / f"db.pickle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gz",
        )
        print("pickle書き込み")
        with gzip.open(data_dir() / "db.pickle.gz", "wb", compresslevel=1) as f:
            pickle.dump(db, f)


if __name__ == "__main__":
    main()
