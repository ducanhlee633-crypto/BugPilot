from fastapi import APIRouter, HTTPException
from schemas import Clone_repo, Delete_folder
from tools.clone_repo import clone_repo
from tools.delete_folder import delete_folder

routers = APIRouter()


@routers.post("/clone")
def clone_repo_endpoint(url: Clone_repo):
    try:
        return {"message": clone_repo(url.url)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clone failed: {e}")

@routers.post("/delete")
def delete_repo_endpoint(folder: Delete_folder):
    try:
        return {"message": delete_folder(folder.folder)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {e}")