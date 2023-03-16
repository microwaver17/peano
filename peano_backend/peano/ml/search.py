from collections import namedtuple
from dataclasses import dataclass

import numpy as np
from fastapi import HTTPException

from peano.db.connect import get_db
from peano.db.models import UID, Image, MLDanbooru, MLTag
from peano.loader import loader
from peano.ml.recognizer import get_recognizer
from peano.ml.states import get_feature_state


@dataclass
class Similarity:
    img_id: UID
    similarity: float


def similar(ws_name: str, query_ids: list[UID]) -> list[Similarity]:
    db = get_db()
    feat_state = get_feature_state()
    feat_state.set_workspace_name(ws_name)

    query_features = []
    for qid in query_ids:
        img_db = db.images.find_one({"id": qid})
        img = Image(**img_db)

        # ML未推論であれば今推論する
        if img.metadata.ml is None:
            print(f"ML推論: {img.id}")
            recog = get_recognizer()
            img_b = loader.get_loader(img).load()
            tags, feature = recog.recognize(img_b, tag_thresh=0.1, tag_max_size=100)
            ml_tags = [MLTag(name=name, weight=weight) for name, weight in tags.items()]
            img.metadata.ml = MLDanbooru(tags=ml_tags, feature=feature)
            db.images.update_one({"id": qid}, {"$set": img.dict()})

        query_features.append(img.metadata.ml.feature)

    mean = feat_state.feat_mean
    feat_mtx = feat_state.feat_mtx

    query_matrix = np.array(query_features)

    # シグモイド関数適用
    query_matrix = 1.0 / (1.0 + np.exp(-query_matrix))

    query_feat = query_matrix.mean(axis=0)
    query_feat -= mean

    print("コサイン類似度算出")
    similar_mtx = np.dot(query_feat, feat_mtx.T) / (
        np.linalg.norm(query_feat) * np.linalg.norm(feat_mtx.T, axis=0)
    )
    print("コサイン類似度算出終了")
    feat_ids = feat_state.feat_ids
    res = [
        Similarity(img_id=img_id, similarity=value)
        for value, img_id in zip(similar_mtx, feat_ids)
    ]

    return res
