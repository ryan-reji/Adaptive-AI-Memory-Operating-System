from pathlib import Path


# Maximum allowed time difference between the filesystem event
# and the nearest foreground activity sample.
MAX_EVENT_TIME_DIFFERENCE = 1.0


def _filename_in_window(file_path, window_title):
    """
    Check whether the file name appears in the foreground
    window title.
    """

    filename = Path(file_path).name.lower().strip()

    if not filename or not window_title:
        return False

    return filename in window_title.lower()


def is_user_interacting_with_file(
    file_path,
    foreground_history,
    event_timestamp
):
    """
    Determine whether a filesystem event corresponds to a file
    that was actually in the foreground at approximately the
    same time.

    Logic:

        filesystem event
                +
        closest foreground state
                +
        filename matches window
                =
            user activity
    """

    if not foreground_history:
        return False

    closest_activity = None
    smallest_difference = float("inf")

    # Find the foreground activity sample closest
    # to the filesystem event.
    for activity in foreground_history:

        timestamp = activity.get("timestamp")

        if timestamp is None:
            continue

        difference = abs(
            timestamp - event_timestamp
        )

        if difference < smallest_difference:
            smallest_difference = difference
            closest_activity = activity

    # No usable foreground sample
    if closest_activity is None:
        return False

    # Event and foreground state are too far apart
    if smallest_difference > MAX_EVENT_TIME_DIFFERENCE:
        return False

    window_title = closest_activity.get(
        "window_title",
        ""
    )

    return _filename_in_window(
        file_path,
        window_title
    )