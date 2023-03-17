from __future__ import annotations

import pickle
from threading import Lock

import numpy as np

from peano.common.pathfinder import data_dir


class FeatureState:
    def __init__(self):
        self.ws_name: str | None = None
        self.feat_mtx: np.ndarray = np.zeros(0)
        self.feat_mean: np.ndarray = np.zeros(0)
        self.feat_ids: list[str] = []

    def clear(self):
        self.ws_name = None
        self.feat_mtx = np.zeros(0)
        self.feat_mean = np.zeros(0)
        self.feat_ids = []

    def set_workspace_name(self, ws_name: str):
        if self.ws_name == ws_name:
            return

        self.ws_name = ws_name
        self.load_from_file()

    def load_from_file(self):
        if self.ws_name is None:
            return
        
        base_dir = data_dir() / self.ws_name

        if (
            not (base_dir / "feature_matrix.npy").exists()
            or not (base_dir / "feature_mean.npy").exists()
            or not (base_dir / "feature_ids.pickle").exists()
        ):
            raise Exception("特徴量ファイルがありません。")

        self.feat_mtx = np.load(str(base_dir / "feature_matrix.npy"))
        self.feat_mean = np.load(str(base_dir / "feature_mean.npy"))
        with open(base_dir / "feature_ids.pickle", "rb") as f:
            self.feat_ids = pickle.load(f)


_feature_state = FeatureState()


def get_feature_state():
    return _feature_state
