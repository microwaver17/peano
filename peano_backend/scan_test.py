import json
import time
from dataclasses import asdict

from peano.common.pathfinder import app_dir
from peano.common.settings import load_settings
from peano.db.manipulate import get_manipulator
from peano.db.models import DB, Workspace
from peano.db import connect
import logging
from peano.scanner import dirscan

logger = logging.getLogger("uvicorn")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    with connect.get_db() as db, get_manipulator(db) as mani:
        if "illust" not in db.workspaces:
            ws = Workspace(
                name="illust",
                # scan_directories=[r"C:\Users\yuya\Documents\devel\peano\samples\dgcv"],
                scan_directories=[r"\\NAS-HOME\nfs_root\illust"],
            )
            mani.add_workspace(ws)

    start_time = time.time()
    dirscan.scan("illust")
    end_time = time.time()
    print("実行時間：{}秒".format(end_time - start_time))

    connect.save_db()

    # with open(app_dir() / "test.json", "w", encoding="utf8") as f:
    #     json.dump(asdict(DB(images)), f, indent=2, ensure_ascii=False)
