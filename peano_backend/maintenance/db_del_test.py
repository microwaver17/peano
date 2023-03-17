import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from peano.db.connect import get_db


def main():
    db = get_db()
    total_count = db.images.count_documents({})

    if input(f"{total_count}件削除しますか？ (y/n)") != "y":
        exit()

    db.images.delete_many({"belong_workspaces": {"$in": ["test"]}})


if __name__ == "__main__":
    main()
