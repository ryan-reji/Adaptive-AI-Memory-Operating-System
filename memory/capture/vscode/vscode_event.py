
from pathlib import Path
from datetime import datetime
import re


def parse_vscode_title(title):
    empty_result = {
        "file": None,
        "file_path": None,
        "project": None
    }

    if not isinstance(title, str) or not title.strip():
        return empty_result.copy()

    title = title.strip()

    suffixes = (
        " - Visual Studio Code Insiders",
        " - Visual Studio Code"
    )

    for suffix in suffixes:
        if title.endswith(suffix):
            title = title[:-len(suffix)].strip()
            break

    # Remove common unsaved/modified indicators.
    title = re.sub(r"^[*●•]+\s*", "", title).strip()
    title = re.sub(r"^\s*-\s*", "", title).strip()

    if not title:
        return empty_result.copy()

    parts = [
        part.strip()
        for part in title.split(" - ")
        if part.strip()
    ]

    if not parts:
        return empty_result.copy()

    invalid_names = {
        "visual studio code",
        "visual studio code insiders",
        "welcome",
        "getting started",
        "unknown"
    }

    first_part = parts[0]

    # Only accept an absolute path if it actually exists.
    if re.match(r"^[A-Za-z]:[\\/]", first_part):
        candidate = Path(first_part)

        if candidate.is_file():
            return {
                "file": candidate.name,
                "file_path": str(candidate.resolve()),
                "project": parts[1] if len(parts) > 1 else None
            }

    # A single title segment is a workspace/window title.
    if len(parts) == 1:
        return {
            "file": None,
            "file_path": None,
            "project": (
                first_part
                if first_part.casefold() not in invalid_names
                else None
            )
        }

    file_name = first_part

    if file_name.casefold() in invalid_names:
        file_name = None

    if file_name and not Path(file_name).suffix:
        file_name = None

    return {
        "file": file_name,
        "file_path": None,
        "project": parts[1] or None
    }


def create_vscode_event(activity):
    parsed = parse_vscode_title(
        activity.get("title", "")
    )

    return {
        "source_type": "vscode",
        "editor": activity.get("editor"),
        "project": parsed["project"],
        "file": parsed["file"],
        "file_path": parsed["file_path"],
        "title": activity.get("title"),
        "started_at": activity["started_at"],
        "ended_at": activity["ended_at"],
        "duration_seconds": activity["duration_seconds"],
        "captured_at": datetime.now().isoformat()
    }
