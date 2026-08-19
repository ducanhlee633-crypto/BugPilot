from pathlib import Path


PROJECT_ROOT = Path("projects").resolve()

def read_file(file:str, folder:str):
    try:
        if file.startswith("."):
            return f"ERROR: This file contains screct keys"
        file = str(file).strip().strip("'\"")
        folder = str(folder).strip().strip("'\"")
        folder_path = (PROJECT_ROOT / folder).resolve()
    
        if not folder_path.is_relative_to(PROJECT_ROOT):
            return f"ERROR: Folder '{folder}' is outside projects/."

        if not folder_path.exists():
            return f"ERROR: Folder '{folder}' does not exist."

        if not folder_path.is_dir():
            return f"ERROR: '{folder}' is not a directory."
        target = (folder_path / file).resolve()
        if not target.is_relative_to(folder_path):
            return f"ERROR: File '{file}' is outside folder '{folder}'."
        if not target.exists():
            return f"ERROR: File '{file}' does not exist in projects/."
        if not target.is_file():
            return f"ERROR: '{file}' is not a file."
        return target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"ERROR: File '{file}' is not a text file."
    except PermissionError:
        return f"ERROR: No permission to read file '{file}'."
    except OSError as e:
        return f"ERROR: Failed to read file '{file}': {e}"
    except Exception as e:
        return f"ERROR: Unexpected error reading file '{file}': {e}"