from datetime import datetime


def parse_vscode_title(title):
    """
    Parse a standard VS Code window title.

    Example:
        vscode_monitor.py - Adaptive-AI-Memory-Operating-System - Visual Studio Code

    Unsaved example:
        ● vscode_monitor.py - Adaptive-AI-Memory-Operating-System - Visual Studio Code

    Returns:
        {
            "file": "vscode_monitor.py",
            "project": "Adaptive-AI-Memory-Operating-System"
        }
    """

    suffixes = [
        " - Visual Studio Code",
        " - Visual Studio Code Insiders"
    ]

    for suffix in suffixes:
        if title.endswith(suffix):
            title = title[:-len(suffix)]
            break

    parts = [part.strip() for part in title.split(" - ")]

    if len(parts) >= 2:
        file_name = parts[0]

        # Remove VS Code's unsaved-change indicator.
        if file_name.startswith("● "):
            file_name = file_name[2:].strip()

        return {
            "file": file_name,
            "project": parts[-1]
        }

    file_name = parts[0] if parts else None

    # Remove VS Code's unsaved-change indicator.
    if file_name and file_name.startswith("● "):
        file_name = file_name[2:].strip()

    return {
        "file": file_name,
        "project": None
    }


def create_vscode_event(activity):
    """
    Convert raw VS Code activity into a standardized event.
    """

    parsed = parse_vscode_title(activity["title"])

    return {
        "source_type": "vscode",
        "editor": activity["editor"],
        "project": parsed["project"],
        "file": parsed["file"],
        "title": activity["title"],
        "started_at": activity["started_at"],
        "ended_at": activity["ended_at"],
        "duration_seconds": activity["duration_seconds"],
        "captured_at": datetime.now().isoformat()
    }