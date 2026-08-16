from pathlib import Path


def write_file(file: str, content: str):
    try:
        file = str(file).strip().strip("'\"")
        path = Path(f"projects/{file}").resolve()
        if "projects" not in path.parts:
            return f"ERROR: Path '{file}' is outside projects/."
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"OK: Wrote {len(content)} chars to '{file}'."
    except PermissionError:
        return f"ERROR: No permission to write file '{file}'."
    except OSError as e:
        return f"ERROR: Failed to write file '{file}': {e}"
    except Exception as e:
        return f"ERROR: Unexpected error writing file '{file}': {e}"

def delete_object_in_file(file: str, content: str):
    try:
        file = str(file).strip().strip("'\"")
        path = Path(f"projects/{file}").resolve()
        if "projects" not in path.parts:
            return f"ERROR: Path '{file}' is outside projects/."
        if not path.exists():
            return f"ERROR: File '{file}' does not exist."
        text = path.read_text(encoding="utf-8")
        if content not in text:
            return f"ERROR: Content '{content[:50]}...' not found in '{file}'."
        path.write_text(text.replace(content, ""), encoding="utf-8")
        return f"OK: Deleted content from '{file}'."
    except PermissionError:
        return f"ERROR: No permission to write file '{file}'."
    except OSError as e:
        return f"ERROR: Failed to write file '{file}': {e}"
    except Exception as e:
        return f"ERROR: Unexpected error writing file '{file}': {e}"
    