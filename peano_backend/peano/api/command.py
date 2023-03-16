from threading import Thread

from fastapi import APIRouter

from peano.api.models import ResultResponse
from peano.db import connect
from peano.ml.preprocess import preprocess
from peano.scanner import dirscan, mlscan

router = APIRouter(prefix="/command", tags=["command"])


@router.post("/dirscan/scan")
def do_dirscan(ws_name: str) -> ResultResponse:
    Thread(target=dirscan.scan, args=(ws_name,)).start()
    return ResultResponse(result=True)


@router.post("/dirscan/scan/stop")
def stop_dirscan() -> ResultResponse:
    dirscan.exit_event.set()
    return ResultResponse(result=True)


@router.post("/mlscan/scan")
def do_mlscan(ws_name: str) -> ResultResponse:
    Thread(target=mlscan.scan, args=(ws_name,)).start()
    return ResultResponse(result=True)


@router.post("/mlscan/scan/stop")
def stop_mlscan() -> ResultResponse:
    mlscan.exit_event.set()
    return ResultResponse(result=True)


@router.post("/mlscan/preprocess")
def do_preprocess(ws_name: str) -> ResultResponse:
    Thread(target=preprocess, args=(ws_name,)).start()
    return ResultResponse(result=True)


@router.post("/db/fix")
def fix_db():
    Thread(target=connect.fix_db).start()
    return ResultResponse(result=True)
