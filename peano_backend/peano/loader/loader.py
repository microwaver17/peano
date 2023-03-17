import hashlib
from abc import abstractmethod, ABC
from io import BytesIO
from pathlib import Path
from functools import lru_cache
from PIL import Image

from peano.common.definitions import THUMBNAIL_SIZE
from peano.common.pathfinder import app_dir
from peano.db.models import SourceType, Image as MImage


class AbstractImageLoader(ABC):
    def __init__(self, path: str):
        self.path = path
        self.thumbnail_dir = app_dir() / "data" / "thumbnail"
        Path(self.thumbnail_dir).mkdir(exist_ok=True, parents=True)

    @abstractmethod
    def load(self) -> bytes:
        pass

    def get_thumbnail_path(self) -> Path:
        file_id = hashlib.md5(self.path.encode("utf8")).hexdigest()
        return Path(self.thumbnail_dir / (file_id + ".jpg"))

    @lru_cache(500)
    def thumbnail(self) -> bytes:
        thumbnail_path = self.get_thumbnail_path()

        if thumbnail_path.exists() is False:
            orig_bio = BytesIO(self.load())
            thumb_bio = BytesIO()

            img = Image.open(orig_bio)
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.thumbnail(THUMBNAIL_SIZE, Image.HAMMING)
            img.save(thumb_bio, format="jpeg", quality=80, optimize=False)

            thumb_b = thumb_bio.getvalue()
            with open(thumbnail_path, "wb") as f:
                f.write(thumb_b)

        else:
            with open(thumbnail_path, "rb") as f:
                thumb_b = f.read()

        return thumb_b


class ImageFileLoader(AbstractImageLoader):
    def load(self):
        with open(self.path, "rb") as f:
            img_b = f.read()

        return img_b


def get_loader(img: MImage) -> AbstractImageLoader:
    if img.source_type == SourceType.file:
        return ImageFileLoader(img.path)

    raise Exception("画像ローダーが実装されていません: " + img.source_type)
