from pathlib import Path


ALLOWED_FOLDERS = [
    Path("memory/tests/test_data").resolve()
]


def is_allowed(file_path):
    file_path = Path(file_path).resolve()

    return any(
        folder == file_path or folder in file_path.parents
        for folder in ALLOWED_FOLDERS
    )


if __name__ == "__main__":
    test_file = "memory/tests/test_data/test.pdf"

    if is_allowed(test_file):
        print("File is allowed.")
    else:
        print("File is NOT allowed.")