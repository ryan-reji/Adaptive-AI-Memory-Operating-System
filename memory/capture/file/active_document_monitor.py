
import os
import re
import time
from pathlib import Path

import psutil

from memory.capture.foreground_activity import (
    get_recent_foreground_activity,
)
from memory.capture.common.permissions import is_allowed
from memory.capture.file.universal_extractor import get_chunk
from memory.capture.file.file_snapshot import create_snapshot
from memory.capture.file.file_evidence import create_file_evidence
from memory.database.activity_evidence_db import save_activity_evidence


SUPPORTED_EXTENSIONS = {
    ".txt", ".md", ".csv", ".json", ".xml", ".yaml", ".yml",
    ".py", ".js", ".ts", ".html", ".css", ".sql",
    ".pdf", ".doc", ".docx", ".odt", ".rtf",
    ".xls", ".xlsx", ".xlsm", ".ods",
    ".ppt", ".pptx", ".odp",
}

APP_TITLE_SUFFIXES = (
    " - ONLYOFFICE",
    " - Microsoft Word",
    " - Word",
    " - Microsoft Excel",
    " - Excel",
    " - Microsoft PowerPoint",
    " - PowerPoint",
    " - WPS Office",
)

SKIP_DIRS = {
    "appdata", ".git", "node_modules", ".venv", "venv",
    "__pycache__", "program files", "windows",
}

# Cache filename lookups so repeated sessions don't rescan folders.
_path_cache = {}


def _filename_from_title(title):
    """Extract a supported filename from a window title."""
    title = title.strip()

    for suffix in APP_TITLE_SUFFIXES:
        if title.lower().endswith(suffix.lower()):
            title = title[:-len(suffix)].strip()

    # Remove common unsaved-document markers.
    title = title.lstrip("*").strip()

    pattern = (
        r'([^\\/:*?"<>|\r\n]+\.'
        r'(?:' + "|".join(
            re.escape(ext.lstrip("."))
            for ext in SUPPORTED_EXTENSIONS
        ) + r'))'
    )

    match = re.search(pattern, title, re.IGNORECASE)
    return match.group(1).strip() if match else None


def _path_from_title(title):
    """Use an absolute path if the application exposes one."""
    pattern = (
        r'([A-Za-z]:\\.*?\.(?:'
        + "|".join(
            re.escape(ext.lstrip("."))
            for ext in SUPPORTED_EXTENSIONS
        )
        + r'))(?=$|\s+-\s)'
    )

    match = re.search(pattern, title, re.IGNORECASE)

    if match:
        candidate = Path(match.group(1))

        if candidate.is_file():
            return candidate.resolve()

    return None


def _path_from_process(pid, filename):
    """Try to find the document among files opened by the app."""
    if not pid or not filename:
        return None

    try:
        process = psutil.Process(pid)

        for opened_file in process.open_files():
            candidate = Path(opened_file.path)

            if (
                candidate.name.lower() == filename.lower()
                and candidate.is_file()
            ):
                return candidate.resolve()

    except (psutil.Error, OSError):
        pass

    return None


def _search_user_folders(filename):
    """
    Search the user's profile for a unique matching filename.
    Ambiguous matches are deliberately rejected.
    """
    if not filename:
        return None

    cache_key = filename.lower()

    if cache_key in _path_cache:
        return _path_cache[cache_key]

    home = Path.home()
    preferred = [
        home / "Downloads",
        home / "Documents",
        home / "Desktop",
        home / "OneDrive",
    ]

    matches = set()

    # Search common folders first.
    for root in preferred:
        if not root.is_dir():
            continue

        for directory, subdirs, files in os.walk(root):
            subdirs[:] = [
                d for d in subdirs
                if d.lower() not in SKIP_DIRS
            ]

            for item in files:
                if item.lower() == cache_key:
                    matches.add(
                        (Path(directory) / item).resolve()
                    )

            if len(matches) > 1:
                break

        if len(matches) > 1:
            break

    # If not found in common folders, search the remaining profile.
    if not matches:
        for directory, subdirs, files in os.walk(home):
            current = Path(directory)

            if current == home:
                subdirs[:] = [
                    d for d in subdirs
                    if d.lower() not in SKIP_DIRS
                    and d not in {
                        "Downloads", "Documents",
                        "Desktop", "OneDrive",
                    }
                ]
            else:
                subdirs[:] = [
                    d for d in subdirs
                    if d.lower() not in SKIP_DIRS
                ]

            for item in files:
                if item.lower() == cache_key:
                    matches.add(
                        (current / item).resolve()
                    )

            if len(matches) > 1:
                break

    result = next(iter(matches)) if len(matches) == 1 else None
    _path_cache[cache_key] = result
    return result


def resolve_document_path(activity):
    """Resolve a document path without guessing between duplicates."""
    title = activity.get("window_title", "")

    path = _path_from_title(title)
    if path:
        return path

    filename = _filename_from_title(title)
    if not filename:
        return None

    path = _path_from_process(
        activity.get("process_id"),
        filename,
    )
    if path:
        return path

    return _search_user_folders(filename)


def capture_active_document(activity, path):
    """Extract and save one active-document evidence record."""
    if not path.is_file() or not is_allowed(path):
        return

    try:
        result = get_chunk(str(path), chunk_number=0)

        event = {
            "source_type": "file",
            "action": "opened",
            "path": str(path),
            "timestamp": time.strftime(
                "%Y-%m-%dT%H:%M:%S",
                time.localtime(activity["timestamp"]),
            ),
        }

        snapshot = create_snapshot(event, result)
        evidence = create_file_evidence(snapshot)
        evidence_id = save_activity_evidence(evidence)

        print(
            f"Saved active-document evidence: "
            f"{path.name} (ID: {evidence_id})"
        )

    except Exception as exc:
        print(
            f"Could not capture active document "
            f"{path.name}: {exc}"
        )



def monitor_active_documents():
    """
    Capture documents opened in supported document applications.
    Skip VS Code because its activity is handled by the VS Code monitor.
    Uses the shared foreground monitor; starts no new thread.
    """
    previous_key = None
    attempted_key = None
    last_attempt = 0.0

    print("Active document monitor started.")

    while True:
        try:
            history = get_recent_foreground_activity()
            activity = history[0] if history else None

            if not activity:
                previous_key = None
                attempted_key = None
                time.sleep(0.5)
                continue

            key = (
                activity.get("hwnd"),
                activity.get("process_id"),
                activity.get("window_title"),
            )

            # Skip VS Code; its activity is captured by its own monitor.
            process_name = (
                activity.get("process_name") or ""
            ).lower()

            if process_name in {"code.exe", "code-insiders.exe"}:
                previous_key = key
                attempted_key = key
                time.sleep(0.5)
                continue

            if key != previous_key:
                previous_key = key
                attempted_key = None
                last_attempt = 0.0

            title = activity.get("window_title", "")
            filename = _filename_from_title(title)

            if (
                filename
                and key != attempted_key
                and time.time() - last_attempt >= 1.0
            ):
                last_attempt = time.time()
                path = resolve_document_path(activity)

                if path:
                    attempted_key = key

                    if is_allowed(path):
                        capture_active_document(activity, path)
                else:
                    # Avoid repeatedly searching for the same document.
                    attempted_key = key

            time.sleep(0.5)

        except Exception as exc:
            print(f"Active document monitor error: {exc}")
            time.sleep(1.0)



if __name__ == "__main__":
    monitor_active_documents()
