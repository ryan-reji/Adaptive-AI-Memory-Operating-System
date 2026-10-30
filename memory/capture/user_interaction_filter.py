
from pathlib import Path

# Keep the stricter threshold for ordinary applications.
MAX_EVENT_TIME_DIFFERENCE = 1.0

# VS Code filesystem events can arrive slightly later than
# the foreground-window sample.
VSCODE_MAX_EVENT_TIME_DIFFERENCE = 5.0

VSCODE_PROCESSES = {
    "code.exe",
    "code-insiders.exe",
}


def _filename_in_window(file_path, window_title):
    filename = Path(file_path).name.casefold().strip()
    title = (window_title or "").casefold()

    return bool(filename and filename in title)


def is_user_interacting_with_file(
    file_path,
    foreground_history,
    event_timestamp
):
    if not foreground_history:
        return False

    filename = Path(file_path).name

    closest_activity = None
    smallest_difference = float("inf")

    for activity in foreground_history:
        timestamp = activity.get("timestamp")

        if timestamp is None:
            continue

        try:
            difference = abs(
                float(timestamp) - float(event_timestamp)
            )
        except (TypeError, ValueError):
            continue

        if difference < smallest_difference:
            smallest_difference = difference
            closest_activity = activity

    if closest_activity is None:
        return False

    process_name = (
        closest_activity.get("process_name") or ""
    ).casefold()

    max_difference = (
        VSCODE_MAX_EVENT_TIME_DIFFERENCE
        if process_name in VSCODE_PROCESSES
        else MAX_EVENT_TIME_DIFFERENCE
    )

    if smallest_difference > max_difference:
        return False

    return _filename_in_window(
        file_path,
        closest_activity.get("window_title", "")
    )
