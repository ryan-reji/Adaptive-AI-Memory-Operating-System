
from pathlib import Path

# Conservative exclusions: never recommend these paths for cleanup.
PROTECTED_DIRECTORY_NAMES = {
    "windows",
    "program files",
    "program files (x86)",
    "programdata",
    "$recycle.bin",
    "system volume information",
}

PROTECTED_FILE_NAMES = {
    "pagefile.sys",
    "hiberfil.sys",
    "swapfile.sys",
}


def get_protection_reason(file_path: str) -> str | None:
    """Return a reason if a path must be excluded from recommendations."""
    path = Path(file_path)

    parts = {part.casefold() for part in path.parts}

    if parts & PROTECTED_DIRECTORY_NAMES:
        return "Protected system or application directory"

    if path.name.casefold() in PROTECTED_FILE_NAMES:
        return "Protected operating-system file"

    return None


def is_protected(file_path: str) -> bool:
    return get_protection_reason(file_path) is not None

