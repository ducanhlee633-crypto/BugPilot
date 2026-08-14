import subprocess
from pathlib import Path


def clone_repo(url:str):
    project = Path("projects")
    result = subprocess.run(["git","clone",url], capture_output = True, text = True, check=True, cwd =project)
    if result.returncode != 0:
        return(result.stderr)    # in cảnh báo
    else:
        return("Clone Successfully")  # return = 0 là successful còn khác là fail
