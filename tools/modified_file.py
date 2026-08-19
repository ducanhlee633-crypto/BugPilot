from pathlib import Path

PROJECT_ROOT = Path("projects").resolve()

def write_file(file: str, content: str, folder: str): #folder = repo
    if file.startswith("."):
        return f"ERROR: This file contains screct keys"
    try:
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
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"OK: Wrote {len(content)} chars to '{file}'."
    except PermissionError:
        return f"ERROR: No permission to write file '{file}'."
    except OSError as e:
        return f"ERROR: Failed to write file '{file}': {e}"
    except Exception as e:
        return f"ERROR: Unexpected error writing file '{file}': {e}"

def delete_object_in_file(file: str, content: str, folder : str):
    try:
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
            return f"ERROR: File '{file}' does not exist."
        text = target.read_text(encoding="utf-8")
        if content not in text:
            return f"ERROR: Content '{content[:50]}...' not found in '{file}'."
        target.write_text(text.replace(content, "", 1), encoding="utf-8")
        return f"OK: Deleted content from '{file}'."
    except PermissionError:
        return f"ERROR: No permission to write file '{file}'."
    except OSError as e:
        return f"ERROR: Failed to write file '{file}': {e}"
    except Exception as e:
        return f"ERROR: Unexpected error writing file '{file}': {e}"
    