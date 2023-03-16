import json
import logging
import pickle
import re
from typing import Literal

from fastapi import APIRouter, Response, Query, HTTPException

from peano.common.pathfinder import resources_dir, data_dir
from peano.db.connect import get_db
from peano.db.models import Image, StrEnum, UID
from peano.api.models import ImageDigest
from peano.loader.loader import get_loader
from peano.ml.search import similar, Similarity

logger = logging.getLogger("uvicorn")


class MIME(StrEnum):
    png = "image/png"
    jpg = "image/jpeg"
    webp = "image/webp"
    gif = "image/gif"

    @staticmethod
    def from_path(path: str):
        if path.endswith(".png"):
            return MIME.png
        elif path.endswith(".jpg"):
            return MIME.jpg
        elif path.endswith(".webp"):
            return MIME.webp
        elif path.endswith(".gif"):
            return MIME.gif

        return MIME.jpg


router = APIRouter(prefix="/image", tags=["image"])

tags_map_en_to_jp: dict[str, str] = {}
tags_map_jp_to_en: dict[str, str] = {}


def initialize():
    global tags_map_en_to_jp, tags_map_jp_to_en

    pkl_path = data_dir() / "class_names_jp_map.json.pickle"
    json_path = resources_dir() / "class_names_jp_map.json"

    if not pkl_path.exists():
        logger.info("JPタグJSON読み込み開始")
        with open(json_path, "r", encoding="utf8") as f:
            tags_map_en_to_jp = json.load(f)
        tags_map_jp_to_en = {
            tag_jp: tag_en for tag_en, tag_jp in tags_map_en_to_jp.items()
        }
        with open(pkl_path, "wb") as f:
            pickle.dump((tags_map_en_to_jp, tags_map_jp_to_en), f, protocol=4)
    else:
        logger.info("JPタグPickle読み込み開始")
        with open(pkl_path, "rb") as f:
            tags_map_en_to_jp, tags_map_jp_to_en = pickle.load(f)
    #
    # with open(json_path, "r", encoding="utf8") as f:
    #     tags_map_en_to_jp = json.load(f)
    # tags_map_jp_to_en = {tag_jp: tag_en for tag_en, tag_jp in tags_map_en_to_jp.items()}

    logger.info("JPタグ読み込み終了")


def make_query_from_keywords(keywords: list[str]) -> list:
    query = []
    for keyword in keywords:
        keyword = keyword.strip()
        if keyword == "":
            continue

        regex = re.compile(keyword)
        query += [
            {"id": keyword},
            {"path": regex},
            {"metadata.tags": regex},
            {"metadata.ml.tags": {"$elemMatch": {"name": regex}}},
        ]

    return query


@router.get("/")
def get(
    ws_name: str,
    start: int,
    end: int,
    keyword: str = None,
    order_by: Literal["id", "date", "random"] = "id",
    order: Literal["asc", "desc"] = "asc",
) -> list[ImageDigest]:
    db = get_db()
    pipeline = []

    query = {}
    query["belong_workspaces"] = ws_name
    if keyword is not None:
        keywords = keyword.replace("　", " ").split(" ")
        q_kwd = make_query_from_keywords(keywords)
        if len(q_kwd) > 0:
            query["$or"] = q_kwd
    pipeline += [{"$match": query}]

    order_num = 1 if order == "asc" else -1
    if order_by == "date":
        pipeline += [{"$sort": {"metadata.last_updated": order_num}}]
    elif order_by == "id":
        pipeline += [{"$sort": {"id": order_num}}]

    if order_by == "random":
        pipeline += [{"$sample": {"size": end - start + 1}}]
        pipeline += [{"$skip": 0}, {"$limit": end - start + 1}]
    else:
        pipeline += [{"$skip": start}, {"$limit": end - start + 1}]

    print(pipeline)

    images = db.images.aggregate(pipeline)

    res = [ImageDigest(id=img["id"]) for img in images]

    return res


@router.get("/similar")
def get_similar_images(
    workspace: str,
    start: int,
    end: int,
    keyword: str = None,
    query_ids: list[UID] = Query(),
    order_by: Literal["similarity"] = "similarity",
    order: Literal["asc", "desc"] = "desc",
) -> list[ImageDigest]:
    db = get_db()

    img_sim = similar(workspace, query_ids)

    if order_by == "similarity":
        img_sim.sort(key=lambda img: img.similarity, reverse=(order == "desc"))

    matched_images: list[Similarity] = []
    for sim in img_sim[start : end + 1]:
        query = {}
        query["id"] = sim.img_id
        if keyword is not None:
            keywords = keyword.replace("　", " ").split(" ")
            q_kwd = make_query_from_keywords(keywords)
            if len(q_kwd) > 0:
                query["$or"] = q_kwd

        if db.images.find_one(query) is None:
            continue

        matched_images.append(sim)
        # if len(matched_images) >= end - start + 1:
        #     break

    return [
        ImageDigest(id=sim.img_id, similarity=sim.similarity) for sim in matched_images
    ]


@router.get("/find")
def find(image_id: str) -> Image:
    db = get_db()

    image_db = db.images.find_one({"id": image_id})
    if image_db is None:
        HTTPException(status_code=404, detail=f"Not Found: {image_id}")

    return Image(**image_db)


@router.get("/file", response_class=Response)
def get_file(image_id: UID, image_type: Literal["original", "thumbnail"] = "original"):
    db = get_db()
    image_db = db.images.find_one({"id": image_id})
    image = Image(**image_db)
    loader = get_loader(image)

    if image_type == "original":
        img_b = loader.load()
        mime = MIME.from_path(image.path)
    else:
        img_b = loader.thumbnail()
        mime = MIME.jpg

    return Response(content=img_b, media_type=mime)


@router.get("/tags/map/jp")
def get_tags_map_jp() -> dict[str, str]:
    return tags_map_en_to_jp
