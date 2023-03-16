from __future__ import annotations

import logging
import re
import time
from datetime import datetime
from pathlib import Path
from itertools import chain
import hashlib
from re import Pattern, Match
from threading import Event, Lock

from peano.common.definitions import AVAILABLE_EXTS
from peano.db.connect import get_db
from peano.db.models import (
    Image,
    SourceType,
    Metadata,
    FileInfo,
    Workspace,
)
from PIL import Image as PImage

logger = logging.getLogger("uvicorn")


def _match_regex(regs: list[Pattern], ss: str) -> list[Match] | None:
    """
    正規表現のリストですべてマッチし、マッチオブジェクトのリストを返す

    見つからなかった (Noneが返ってきた) マッチオブジェクトは返り値のリストには含まない

    Args:
        regs: 検査する正規表現
        ss: マッチさせる文字列

    Returns:
        マッチオブジェクトのリスト （見つからなければNone）

    """
    matched = list(
        filter(
            lambda mtc: mtc is not None,
            [exp.search(ss) for exp in regs],
        )
    )

    return matched if len(matched) != 0 else None


def _calc_md5(path: Path | str, limit: int = -1) -> str:
    with open(path, "rb") as f:
        digest = hashlib.md5(f.read(limit)).hexdigest()

    return digest


exit_event = Event()
re_entry_lock = Lock()


def scan(workspace_name: str):
    """
    ディレクトリをスキャン

    重複ファイルは除外される

    Args:
        workspace_name: ワークスペース名
    """

    if re_entry_lock.locked():
        print(f"すでにスキャンが実行しています")
        return

    with re_entry_lock:
        print(f"スキャン開始 {workspace_name}")

        db = get_db()
        workspace_db = db.workspaces.find_one({"name": workspace_name})
        workspace = Workspace(**workspace_db)
        re_ignores = [re.compile(ign) for ign in workspace.ignore_patterns]
        prev_time = time.time()

        # ----- DBからファイルの削除 -----
        total_count_list = list(
            db.images.aggregate(
                [{"$match": {"belong_workspaces": workspace_name}}, {"$count": "total"}]
            )
        )
        if len(total_count_list) > 0:
            total_count = total_count_list[0]["total"]
        else:
            total_count = 0

        del_count = 0
        for i, img in enumerate(db.images.find({"belong_workspaces": workspace_name})):
            if exit_event.is_set():
                exit_event.clear()
                print("中断しました。")
                return

            # 経過表示
            now = time.time()
            if now - prev_time > 1:
                print(
                    f"[db del files] {i + 1}/{total_count}件 ...{str(img['path'])[-60:]}"
                )
                prev_time = now

            # 無視リストとマッチング
            if _match_regex(re_ignores, str(img["path"])) is not None:
                db.images.update_one(
                    {"id": img["id"]},
                    {"$pull": {"belong_workspaces": workspace_name}},
                )

            if not Path(img["path"]).exists():
                # print(f"ファイルが存在しません: {img['path'][-100:]}")
                db.images.delete_one({"id": img["id"]})
                del_count += 1

        # ----- 1. ファイルの列挙 -----

        # ファイル一覧と無視条件を取得
        total_count_list = list(
            db.images.aggregate(
                [
                    {"$match": {"belong_workspaces": workspace_name}},
                    {"$group": {"_id": "total", "count": {"$sum": 1}}},
                ]
            )
        )
        if len(total_count_list) > 0:
            total_count = total_count_list[0]["total"]
        else:
            total_count = 0

        add_count = 0
        for i, path_rel in enumerate(
            chain.from_iterable(
                [Path(p).glob("**/*") for p in workspace.scan_directories]
            )
        ):
            if exit_event.is_set():
                exit_event.clear()
                print("中断しました。")
                return

            path = path_rel.resolve()
            if path.suffix not in AVAILABLE_EXTS or path.is_dir():
                continue

            now = time.time()
            if now - prev_time > 1:
                print(f"[add files] {i + 1}/{total_count}件 ...{str(path)[-60:]}")
                prev_time = now

            # 無視リストとマッチング
            if _match_regex(re_ignores, str(path)) is not None:
                continue

            # すでにあればワークスペースを追加するだけ
            exist_img = db.images.find_one({"path": str(path)})
            if exist_img is not None:
                if workspace_name not in exist_img["belong_workspaces"]:
                    db.images.update_one(
                        {"path": str(path)},
                        {"$push": {"belong_workspaces": workspace_name}},
                    )
                continue

            # エントリ作成
            file_info = FileInfo(
                file_size=path.stat().st_size,
            )
            metadata = Metadata(
                file_info=file_info,
                last_updated=datetime.fromtimestamp(path.stat().st_mtime),
            )

            # 画像サイズ取得
            img_pil = PImage.open(path)
            metadata.image_size = img_pil.size

            image = Image(
                source_type=SourceType.file,
                path=str(path),
                metadata=metadata,
                belong_workspaces=[workspace_name],
            )
            db.images.insert_one(image.dict())

            add_count += 1

        # ----- 2.重複ファイルの除外 -----

        # ファイルサイズが重複している画像を集計
        #  ________________
        # |  size  | count |
        # |--------|-------|
        # | 1000KB |   1   |  <- 1は重複していない
        # | 1500KB |   4   |  <- 4件の画像が同じファイルサイズ
        # | 1700KB |   2   |
        #  ^^^^^^^^^^^^^^^^
        # images_by_count = db.images.aggregate(
        #     [
        #         {"belong_workspaces": {"$in": [workspace_name]}},
        #         {
        #             "_id": "$metadata.file_info.file_size",
        #             "count": {"$sum": {"$toInt": 1}},
        #         },
        #     ]
        # )
        # for dup_size in images_by_count["_id"]:
        #
        #
        # # サイズが重複しているものはMD5ハッシュで比較
        dup_count = 0
        # for i, dup_size_img in enumerate(duplicated_size_image):
        #     if exit_event.is_set():
        #         exit_event.clear()
        #         print("中断しました。")
        #         return
        #
        #     # 経過表示
        #     now = time.time()
        #     if now - prev_time > 1:
        #         progress = int(100 * i / duplicated_size_count)
        #         prev_time = now
        #         print(f"[2/3] {progress:3}% ...{str(dup_size_img.path)[-60:]}")
        #     if now - last_save_time > 120:
        #         connect.save_db_async()
        #         last_save_time = now
        #
        #     with connect.get_db() as db, get_manipulator(db) as mani:
        #         # ハッシュ計算し一致する画像を取得
        #         if dup_size_img.metadata.file_info.md5_hash == "":
        #             hash = _calc_md5(dup_size_img.path)
        #             dup_size_img.metadata.file_info.md5_hash = hash
        #         else:
        #             hash = dup_size_img.metadata.file_info.md5_hash
        #         dp = [
        #             img
        #             for img in images_after_scan
        #             if img.metadata.file_info.md5_hash == hash
        #         ]
        #         # 重複ありの場合
        #         if len(dp) >= 2:  # （自分も含めるので >= 2）
        #             workspace.ignore_image_ids.append(dup_size_img.id)
        #             dup_count += 1

        print(f"スキャン終了 {workspace_name}")
        print(f"{add_count}件発見 {dup_count}件重複 {del_count}件削除")

        return
