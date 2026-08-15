from pathlib import Path


def list_files(folder):
    folder = str(folder).strip().strip("'\"").rstrip("/")
    path = Path(f"projects/{folder}")
    return [item.name for item in path.iterdir()]

