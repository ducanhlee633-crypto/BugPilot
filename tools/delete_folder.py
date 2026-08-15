import subprocess
from pathlib import Path


def delete_folder(folder: str):
    project = Path("projects")
    project.mkdir(exist_ok=True)
    result = subprocess.run(["rm", "-rf", folder], capture_output=True, text=True, check=False, cwd=project)
    if result.returncode != 0:
        return(result.stderr)
    else:
        return("Deleted Successfully")
