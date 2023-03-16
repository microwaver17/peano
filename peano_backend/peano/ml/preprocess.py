import pickle

import numpy as np

from peano.common.pathfinder import data_dir
from peano.db.connect import get_db
from peano.ml.states import get_feature_state


def preprocess(ws_name: str):
    """特徴ベクトルを平均で引く"""

    db = get_db()

    base_dir = data_dir() / ws_name
    base_dir.mkdir(exist_ok=True)

    print("DBからベクトル取得")

    query = {"belong_workspaces": ws_name, "metadata.ml": {"$ne": None}}
    images = db.images.find(query)
    images_count = db.images.count_documents(query)

    feat_mtx = np.empty((images_count, 512), dtype=np.float32)
    feat_ids: list[str] = []
    for row, img in enumerate(images):
        feat_mtx[row] = np.array(img["metadata"]["ml"]["feature"], dtype=np.float32)
        feat_ids.append(img["id"])

    print("シグモイド関数適用")
    feat_mtx = 1.0 / (1.0 + np.exp(-feat_mtx))

    print("特徴ベクトル平均計算")
    feat_mean = np.mean(feat_mtx, axis=0)
    feat_mtx -= feat_mean

    print("行列を保存")
    np.save(str(base_dir / "feature_matrix.npy"), feat_mtx)
    np.save(str(base_dir / "feature_mean.npy"), feat_mean)
    with open(base_dir / "feature_ids.pickle", "wb") as f:
        pickle.dump(feat_ids, f, 4)

    get_feature_state().clear()

    print("完了")
    return
