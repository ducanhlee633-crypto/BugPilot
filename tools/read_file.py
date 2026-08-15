from pathlib import Path


def read_file(file):
    try:
        file = str(file).strip().strip("'\"")
        path = Path(f"projects/{file}")
        if not path.exists():
            return f"ERROR: File '{file}' does not exist in projects/."
        if not path.is_file():
            return f"ERROR: '{file}' is not a file."
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"ERROR: File '{file}' is not a text file."
    except PermissionError:
        return f"ERROR: No permission to read file '{file}'."
    except OSError as e:
        return f"ERROR: Failed to read file '{file}': {e}"
    except Exception as e:
        return f"ERROR: Unexpected error reading file '{file}': {e}"
