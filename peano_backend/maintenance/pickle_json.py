import argparse
import gzip
import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pickle

from peano.db.models import DB
from peano.common.pathfinder import data_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "output_type", type=str, help="出力形式", choices=["json", "pickle", "bench"]
    )
    args = parser.parse_args()

    if args.output_type == "bench":
        print("pickle読み込み")
        with open(data_dir() / "db.pickle", "rb") as f:
            db: DB = pickle.load(f)

        for i in range(1, 9):
            print(f"pickle書き出し: 圧縮率: {i}")
            start = time.time()
            with gzip.open(
                data_dir() / f"db_bench_{i}.pickle.gz", "wb", compresslevel=i
            ) as f:
                pickle.dump(db, f, 5)
            end = time.time()
            print(f"時間: {end - start}")
            print()
    elif args.output_type == "pickle":
        print("JSON読み込み")
        with open(data_dir() / "db.json", "r", encoding="utf8") as f:
            db = DB.parse_raw(f.read())
        print("pickle書き出し")
        with gzip.open(data_dir() / "db_export.pickle.gz", "wb", compresslevel=1) as f:
            pickle.dump(db, f, 5)
    else:
        print("pickle読み込み")
        with gzip.open(data_dir() / "db.pickle.gz", "rb") as f:
            db: DB = pickle.load(f)
        print("JSON書き出し")
        with open(data_dir() / "db_export.json", "w", encoding="utf8") as f:
            f.write(db.json(indent=2, ensure_ascii=False))
