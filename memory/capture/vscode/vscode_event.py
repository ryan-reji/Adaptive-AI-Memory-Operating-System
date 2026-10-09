
from pathlib import Path
from datetime import datetime
import re


def parse_vscode_title(title):
    """
    Parse a VS Code window title into project, filename,
    and absolute file path.

    Supports titles such as:
      C:\\project\\src\\main.py - project - Visual Studio Code
      main.py - project - Visual Studio Code
      project - Visual Studio Code
    """
    if not title or not title.strip():
        return {
            "file": None,
            "file_path": None,
            "project": None
        }

    title = title.strip()

    # Remove the VS Code application suffix.
    suffixes = [
        " - Visual Studio Code Insiders",
        " - Visual Studio Code"
    ]

    for suffix in suffixes:
        if title.endswith(suffix):
            title = title[:-len(suffix)].strip()
            break

    # Remove unsaved-file indicator.
    title = re.sub(r"^●\s*", "", title).strip()

    # A title beginning with a separator means there is no
    # active editor filename.
    if not title or title.startswith(" - "):
        return {
            "file": None,
            "file_path": None,
            "project": None
        }

    # Split the title into editor and workspace portions.
    parts = [part.strip() for part in title.split(" - ") if part.strip()]

    if not parts:
        return {
            "file": None,
            "file_path": None,
            "project": None
        }

    first_part = parts[0]

    # A Windows absolute path should be preserved as the file path.
    if re.match(r"^[A-Za-z]:[\\/]", first_part):
        candidate = Path(first_part)

        file_path = str(candidate.resolve())
        file_name = candidate.name
        project = parts[1] if len(parts) >= 2 else None

        return {
            "file": file_name or None,
            "file_path": file_path,
            "project": project or None
        }

    # Reject titles that look like workspace-only titles rather
    # than filenames.
    if len(parts) == 1:
        return {
            "file": None,
            "file_path": None,
            "project": parts[0] or None
        }

    file_name = first_part
    project = parts[1] or None

    # Ignore common window-title placeholders.
    invalid_names = {
        "visual studio code",
        "visual studio code insiders",
        "untitled",
        "welcome"
    }

    if file_name.lower() in invalid_names:
        file_name = None

    return {
        "file": file_name,
        "file_path": None,
        "project": project
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
