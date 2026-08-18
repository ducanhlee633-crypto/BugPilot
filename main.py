from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from routers import agent, modified_repo 

app = FastAPI()

PROJECTS_DIR = Path("projects")
app.include_router(agent.router, prefix = "/call_agent", tags = ["agent"])
app.include_router(modified_repo.routers, prefix = "/repo", tags = ["modified_repo"] )

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