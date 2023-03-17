import os
from enum import Enum
from itertools import chain


class ImageType(str, Enum):
    PNG = ".png"
    JPG = ".jpg"
    GIF = ".gif"


class DocumentType(str, Enum):
    PDF = ".pdf"


class ScanSourceType(str, Enum):
    DIRECTORY = "directory"


AVAILABLE_EXTS = list(chain(ImageType))


THUMBNAIL_SIZE = (300, 300)
API_URL_ROOT = "/api"

TAG_THRESH = 0.1
TAG_MAX_SIZE = 100

PORT = 17713
PORT_OFFLOAD = 17714

OFFLOAD_URL_LOCAL = "http://127.0.0.1:17714"
OFFLOAD_URL_REMOTE = os.environ.get("PEANO_OFFLOAD_URL_REMOTE", "")
