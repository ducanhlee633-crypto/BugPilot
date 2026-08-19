from pathlib import Path


PROJECT_ROOT = Path("projects").resolve()

def list_files(folder):
    try:
        folder = str(folder).strip().strip("'\"").rstrip("/")
        path = (PROJECT_ROOT / folder).resolve()
        if not path.is_relative_to(PROJECT_ROOT):
            return f"ERROR: Folder '{folder}' is outside projects/."
        if not path.exists():
            return f"ERROR: Folder '{folder}' does not exist in projects/."
        if not path.is_dir():
            return f"ERROR: '{folder}' is not a directory."
        return [item.name for item in path.iterdir()]
    except PermissionError:
        return f"ERROR: No permission to read folder '{folder}'."
    except OSError as e:
        return f"ERROR: Failed to read folder '{folder}': {e}"
    except Exception as e:
        return f"ERROR: Unexpected error reading folder '{folder}': {e}"
