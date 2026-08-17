from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from schemas import Clone_repo, Delete_folder, Prompt
from tools.clone_repo import clone_repo
from tools.delete_folder import delete_folder
from agent import call_tool

app = FastAPI()

PROJECTS_DIR = Path("projects")


@app.get("/", include_in_schema=False)
def ui():
    return FileResponse("ui/index.html")


@app.get("/repos", include_in_schema=False)
def list_repos():
    PROJECTS_DIR.mkdir(exist_ok=True)
    return sorted(
        p.name for p in PROJECTS_DIR.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    )


app.mount("/static", StaticFiles(directory="ui"), name="static")


@app.post("/clone_repo")
def clone_repo_endpoint(url: Clone_repo):
    try:
        return {"message": clone_repo(url.url)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clone failed: {e}")


@app.post("/delete_repo")
def delete_repo_endpoint(folder: Delete_folder):
    try:
        return {"message": delete_folder(folder.folder)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {e}")


@app.post("/call_agent")
async def call_agent_endpoint(prompt: Prompt):
    try:
        return await call_tool(prompt)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")