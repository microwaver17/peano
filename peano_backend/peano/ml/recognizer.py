from __future__ import annotations
import gzip

import io
import json
import shutil
from pathlib import Path
from threading import Lock
from typing import Literal

from torch import Tensor
from torch.fx import GraphModule
from torchvision.models.feature_extraction import create_feature_extractor

from peano.common.pathfinder import data_dir, resources_dir
from torchvision import transforms

import torch
import logging
from PIL import Image, ImageFile

from peano.ml.danbooru_resnet import resnet18, resnet34, resnet50

# 巨大な画像ファイルでも読み込む
ImageFile.LOAD_TRUNCATED_IMAGES = True

logger = logging.getLogger("uvicorn")


class _AnimeRecognizer:
    MODEL_MAP = {
        "resnet18": {
            "builder": resnet18,
            "class_file": "class_names_100.json",
            # "mean": [0.485, 0.456, 0.406],
            # "std": [0.229, 0.224, 0.225],
            "mean": [0.5422357320785522, 0.5034515261650085, 0.49635425209999084],
            "std": [0.40316540002822876, 0.39340198040008545, 0.3892141580581665],
        },
        "resnet34": {
            "builder": resnet34,
            "class_file": "class_names_500.json",
            # "mean": [0.485, 0.456, 0.406],
            # "std": [0.229, 0.224, 0.225],
            "mean": [0.5422357320785522, 0.5034515261650085, 0.49635425209999084],
            "std": [0.40316540002822876, 0.39340198040008545, 0.3892141580581665],
        },
        "resnet50": {
            "builder": resnet50,
            "class_file": "class_names_6000.json",
            "mean": [0.714, 0.663, 0.652],
            "std": [0.297, 0.302, 0.298],
        },
    }
    NODE_NAME_FEATURE = "1.5"
    NODE_NAME_TAGS = "1.8"

    def __init__(self, model_name: Literal["resnet18", "resnet34", "resnet50"]):
        self._model_name = model_name
        self._model = None
        self._extractor: GraphModule | None = None
        self._preprocess = None
        self._class_name = None
        self._class_name_jp_map = None

    def load_model(self):
        if self._model_name not in self.MODEL_MAP:
            raise Exception(
                f"モデル名 {self._model_name} が不正です。有効なモデル名: ",
                ", ".join(self.MODEL_MAP.keys()),
            )
        self._model = self.MODEL_MAP[self._model_name]["builder"]()
        self._model.eval()

        # 中間層を出力できるようにする
        self._extractor = create_feature_extractor(
            self._model, [self.NODE_NAME_FEATURE, self.NODE_NAME_TAGS]
        )

        with open(
            resources_dir() / self.MODEL_MAP[self._model_name]["class_file"],
            "r",
            encoding="utf8",
        ) as f:
            self._class_name = json.load(f)
        with open(
            resources_dir() / "class_names_jp_map.json",
            "r",
            encoding="utf8",
        ) as f:
            self._class_name_jp_map = json.load(f)

        self._preprocess = transforms.Compose(
            [
                transforms.Resize(360),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=self.MODEL_MAP[self._model_name]["mean"],
                    std=self.MODEL_MAP[self._model_name]["std"],
                ),
            ]
        )

    def _recognize_tags(
        self, output: Tensor, thresh: float, max_size: int
    ) -> dict[str, float]:
        probs = torch.sigmoid(output[0])

        res = {}
        stop = min(len(probs[probs > thresh]), max_size)
        idxs = probs.argsort(descending=True)
        for i in idxs[:stop]:
            class_name = self._class_name[i]
            value = probs[i].cpu().numpy().item()
            res[class_name] = value

        return res

    def _recognize_feature(self, output: Tensor) -> list[float]:
        probs = output[0]
        res = []
        for i, v in enumerate(probs):
            res.append(float(v.cpu()))
        return res

    def recognize_make_batch(self, img_b: bytes) -> Tensor:
        buf = io.BytesIO(img_b)
        img = Image.open(buf)
        if img.mode != "RGB":
            img = img.convert("RGB")
        tensor = self._preprocess(img)
        batch = tensor.unsqueeze(0)
        return batch

    def recognize_batch(
        self, batch: Tensor, tag_thresh, tag_max_size
    ) -> tuple[dict[str, float], list[float]]:
        if torch.cuda.is_available():
            batch = batch.to("cuda")
            self.model.to("cuda")
        with torch.no_grad():
            output = self._extractor(batch)
            output_tags = output[self.NODE_NAME_TAGS]
            output_feature = output[self.NODE_NAME_FEATURE]

        tags = self._recognize_tags(
            output_tags, thresh=tag_thresh, max_size=tag_max_size
        )
        feature = self._recognize_feature(output_feature)

        return tags, feature

    def recognize(
        self, img_b: bytes, tag_thresh, tag_max_size
    ) -> tuple[dict[str, float], list[float]]:
        batch = self.recognize_make_batch(img_b)
        tags, feature = self.recognize_batch(batch, tag_thresh, tag_max_size)
        return tags, feature


_recognizer: _AnimeRecognizer | None = None

_lock_change_recognizer = Lock()


def get_recognizer() -> _AnimeRecognizer:
    global _recognizer

    with _lock_change_recognizer:
        if _recognizer is None:
            logger.info("Recognizer初期化開始")

            _recognizer = _AnimeRecognizer("resnet50")
            _recognizer.load_model()

            logger.info("Recognizer初期化終了")

    return _recognizer


def init_torch_hub():
    torch.hub.set_dir(str(data_dir() / "pytorch_hub"))
    if not (data_dir() / "pytorch_hub").exists():
        # エラーが出るので、一旦load実行して、ファイルを差し替える
        try:
            torch.hub.load("RF5/danbooru-pretrained", "resnet50")
        except Exception as e:
            print(e)

        shutil.copyfile(
            Path(__file__).parent / "danbooru_resnet.py",
            data_dir()
            / "pytorch_hub"
            / "RF5_danbooru-pretrained_master"
            / "danbooru_resnet.py",
        )
        torch.hub.load("RF5/danbooru-pretrained", "resnet50")


if __name__ == "__main__":
    pass
    # logging.basicConfig(level=logging.INFO)
    #
    # parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "depth", choices=["50", "34", "18", "50_feature"], help="depth of ResNet"
    # )
    # args = parser.parse_args()
    #
    # sample_dir = app_dir() / "sample"
    # sample_imgs = load_samples(sample_dir)
    #
    # model_name = f"resnet{args.depth}"
    # recognizer = AnimeRecognizer(model_name)
    # recognizer.load_model()
    #
    # path_feature = []
    # for i, img in enumerate(sample_imgs):
    #     for path in img.paths:
    #         print(f"[{i} / {len(sample_imgs)}] {path}")
    #         ml = recognizer.recognize(path)
    #         features_dict = asdict(ml)
    #
    #         path_feature.append([path.name, features_dict])
    #
    # with open(app_dir() / f"tags_{model_name}.json", "w", encoding="utf8") as f:
    #     json.dump(path_feature, f, ensure_ascii=False, indent=4)
