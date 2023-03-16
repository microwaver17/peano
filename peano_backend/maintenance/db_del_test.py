import os
import sys

from peano.db.connect import get_db

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


def main():
    db = get_db()
    total_count = db.images.aggregate(
        {"_id": "total", "count": {"$sum": {"$toInt": 1}}}
    )

    if input(f"{total_count['count']}件削除しますか？ (y/n)") != "y":
        exit()

    db.images.delete_many({"belong_workspaces": {"$in": ["test"]}})


if __name__ == "__main__":
    main()
