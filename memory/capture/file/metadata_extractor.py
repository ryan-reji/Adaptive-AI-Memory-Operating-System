from pathlib import Path
from datetime import datetime


def extract_metadata(file_path):
    path = Path(file_path)
    stat = path.stat()

    return {
        "file_name": path.name,
        "extension": path.suffix.lower(),
        "file_path": str(path.resolve()),
        "file_size": stat.st_size,
        "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat()
    }


if __name__ == "__main__":
    test_file = "memory/tests/test_data/test.py"

    metadata = extract_metadata(test_file)

    print("Metadata:")
    print(metadata)