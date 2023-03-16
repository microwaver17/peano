from fastapi import APIRouter, HTTPException

from peano.db.connect import get_db
from peano.db.models import Workspace
from peano.api.models import ResultResponse

router = APIRouter(prefix="/workspace", tags=["workspace"])


@router.get("/find")
def find(ws_name: str) -> Workspace:
    db = get_db()
    return db.workspaces.find_one({"name": ws_name})


@router.get("/")
def get() -> dict[str, Workspace]:
    db = get_db()
    workspaces_db = db.workspaces.find()
    res = {wdb["name"]: Workspace(**wdb) for wdb in workspaces_db}
    return res


@router.post("/update")
def update(workspace: Workspace) -> ResultResponse:
    db = get_db()

    if db.workspaces.find_one({"name": workspace.name}) is None:
        raise HTTPException(400, detail="Workspaceが存在しません: " + workspace.name)

    db.workspaces.update_one({"name": workspace.name}, {"$set": workspace.dict()})

    return ResultResponse(result=True)


@router.post("/create")
def create(workspace: Workspace) -> ResultResponse:
    db = get_db()

    if db.workspaces.find_one({"name": workspace.name}) is not None:
        raise HTTPException(400, detail="Workspaceがすでに存在します: " + workspace.name)

    db.workspaces.insert_one(workspace.dict())

    return ResultResponse(result=True)


@router.post("/delete")
def delete(workspace: Workspace) -> ResultResponse:
    db = get_db()

    if db.workspaces.find_one({"name": workspace}) is None:
        raise HTTPException(400, detail="Workspaceが存在しません: " + workspace.name)

    db.workspaces.delete_one({"name": workspace})

    return ResultResponse(result=True)
