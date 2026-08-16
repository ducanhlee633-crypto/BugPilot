import shutil
from pathlib import Path


def delete_folder(folder: str):
    project = Path("projects").resolve()
    project.mkdir(exist_ok=True)
    folder = str(folder).strip().strip("'\"")
    target = (project / folder).resolve()
    if target == project or project not in target.parents:
        return f"ERROR: Path '{folder}' is outside projects/."
    if not target.exists():
        return f"ERROR: Folder '{folder}' does not exist."
    shutil.rmtree(target)
    return "Deleted Successfully"