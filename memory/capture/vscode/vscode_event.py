
from pathlib import Path
from datetime import datetime
import re


def parse_vscode_title(title):
    """
    Parse a VS Code window title into project, filename,
    and absolute file path when available.
    """
    empty_result = {
        "file": None,
        "file_path": None,
        "project": None
    }

    if not title or not title.strip():
        return empty_result.copy()

    title = title.strip()

    # Remove VS Code application suffix.
    suffixes = (
        " - Visual Studio Code Insiders",
        " - Visual Studio Code"
    )

    for suffix in suffixes:
        if title.endswith(suffix):
            title = title[:-len(suffix)].strip()
            break

    # Remove common unsaved/modified indicators.
    title = re.sub(r"^[●*]\s*", "", title).strip()

    if not title:
        return empty_result.copy()

    # VS Code can show a workspace-only title.
    if title.startswith(" - "):
        return empty_result.copy()

    parts = [part.strip() for part in title.split(" - ")]

    if not parts or not parts[0]:
        return empty_result.copy()

    first_part = parts[0]

    invalid_names = {
        "visual studio code",
        "visual studio code insiders",
        "welcome",
        "getting started"
    }

    # Handle a title containing an absolute Windows file path.
    if re.match(r"^[A-Za-z]:[\\/]", first_part):
        candidate = Path(first_part)

        return {
            "file": candidate.name or None,
            "file_path": str(candidate.resolve()),
            "project": parts[1] if len(parts) > 1 else None
        }

    # A single title segment is not enough to establish
    # that the active editor contains a file.
    if len(parts) < 2:
        return {
            "file": None,
            "file_path": None,
            "project": first_part or None
        }

    file_name = first_part

    if file_name.lower() in invalid_names:
        file_name = None

    # Do not treat a workspace-only title as a file.
    if file_name and not Path(file_name).suffix:
        file_name = None

    return {
        "file": file_name,
        "file_path": None,
        "project": parts[1] or None
    }


def create_vscode_event(activity):
    parsed = parse_vscode_title(activity.get("title", ""))

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
