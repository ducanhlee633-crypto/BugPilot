from pathlib import Path



def read_file(file):
    path = Path(f"projects/{file}")
    return path.read_text()
