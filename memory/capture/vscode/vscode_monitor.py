import time
from datetime import datetime
from memory.capture.vscode.vscode_event import create_vscode_event
from memory.capture.vscode.vscode_aggregator import aggregate_vscode_event
from memory.capture.vscode.vscode_snapshot import create_vscode_snapshot

import psutil
import win32gui
import win32process


SUPPORTED_EDITORS = {
    "code.exe": "VS Code",
    "code-insiders.exe": "VS Code Insiders"
}


def get_active_window():
    """
    Get information about the currently active window.

    Returns:
        dict | None
    """
    hwnd = win32gui.GetForegroundWindow()

    if not hwnd:
        return None

    title = win32gui.GetWindowText(hwnd)

    if not title:
        return None

    _, pid = win32process.GetWindowThreadProcessId(hwnd)

    try:
        process = psutil.Process(pid)
        process_name = process.name().lower()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

    editor = SUPPORTED_EDITORS.get(process_name)

    if not editor:
        return None

    return {
        "editor": editor,
        "title": title,
        "window_handle": hwnd,
        "timestamp": datetime.now().isoformat()
    }


def monitor():
    """
    Monitor VS Code activity and print completed activity intervals.
    """

    previous_activity = None
    start_time = None

    print("VS Code monitor started...")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:

            current_activity = get_active_window()

            # VS Code is not currently active
            if current_activity is None:

                if previous_activity is not None:
                    finish_activity(previous_activity, start_time)

                    previous_activity = None
                    start_time = None

                time.sleep(1)
                continue

            # First VS Code activity
            if previous_activity is None:

                previous_activity = current_activity
                start_time = datetime.now()

            # VS Code window/title changed
            elif (
                current_activity["window_handle"]
                != previous_activity["window_handle"]
                or current_activity["title"]
                != previous_activity["title"]
            ):

                finish_activity(previous_activity, start_time)

                previous_activity = current_activity
                start_time = datetime.now()

            time.sleep(1)

    except KeyboardInterrupt:

        if previous_activity is not None:
            finish_activity(previous_activity, start_time)

        print("\nVS Code monitor stopped.")


def finish_activity(activity, start_time):
    """
    Finish raw VS Code activity and run it through
    the complete event → aggregation → snapshot pipeline.
    """

    end_time = datetime.now()

    duration = (end_time - start_time).total_seconds()

    raw_activity = {
        "editor": activity["editor"],
        "title": activity["title"],
        "started_at": start_time.isoformat(),
        "ended_at": end_time.isoformat(),
        "duration_seconds": round(duration, 2)
    }

    # Create standardized event
    event = create_vscode_event(raw_activity)

    # Aggregate and persist in SQLite
    aggregated = aggregate_vscode_event(event)

    # Create compact snapshot
    snapshot = create_vscode_snapshot(aggregated)

    print(snapshot)


if __name__ == "__main__":
    monitor()