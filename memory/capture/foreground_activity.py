import ctypes
import time
import threading
from ctypes import wintypes
from collections import deque

import psutil


user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("dwTime", wintypes.DWORD),
    ]


# Keep the last 2 seconds of foreground activity.
_HISTORY_SECONDS = 5.0
_history = deque()
_lock = threading.Lock()


def get_foreground_window():

    hwnd = user32.GetForegroundWindow()

    if not hwnd:
        return None

    process_id = wintypes.DWORD()

    user32.GetWindowThreadProcessId(
        hwnd,
        ctypes.byref(process_id)
    )

    length = user32.GetWindowTextLengthW(hwnd)

    title_buffer = ctypes.create_unicode_buffer(
        length + 1
    )

    user32.GetWindowTextW(
        hwnd,
        title_buffer,
        length + 1
    )

    process_name = ""

    try:
        process_name = psutil.Process(
            process_id.value
        ).name()

    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied
    ):
        pass

    return {
        "hwnd": hwnd,
        "process_id": process_id.value,
        "process_name": process_name,
        "window_title": title_buffer.value,
    }


def get_last_input_seconds():

    last_input = LASTINPUTINFO()
    last_input.cbSize = ctypes.sizeof(
        LASTINPUTINFO
    )

    if not user32.GetLastInputInfo(
        ctypes.byref(last_input)
    ):
        return None

    current_tick = kernel32.GetTickCount()

    elapsed_ms = (
        current_tick - last_input.dwTime
    ) & 0xFFFFFFFF

    return elapsed_ms / 1000.0


def get_foreground_activity():

    window = get_foreground_window()

    if window is None:
        return None

    return {
        **window,
        "last_input_seconds": (
            get_last_input_seconds()
        ),
        "timestamp": time.time(),
    }


def _record_foreground_activity():

    activity = get_foreground_activity()

    if activity is None:
        return

    now = time.time()

    with _lock:

        _history.append(activity)

        # Remove entries older than 2 seconds.
        while (
            _history
            and now - _history[0]["timestamp"]
            > _HISTORY_SECONDS
        ):
            _history.popleft()


def start_foreground_monitor():

    """
    Continuously record foreground activity.
    """

    while True:

        try:
            _record_foreground_activity()

        except Exception as e:
            print(
                f"Foreground monitor error: {e}"
            )

        time.sleep(0.05)


def get_recent_foreground_activity():

    """
    Return recent foreground activity history.

    Newest activity is first.
    """

    with _lock:

        now = time.time()

        # Remove old entries.
        while (
            _history
            and now - _history[0]["timestamp"]
            > _HISTORY_SECONDS
        ):
            _history.popleft()

        return list(reversed(_history))


if __name__ == "__main__":

    print(
        "Foreground activity history monitor started."
    )

    monitor_thread = threading.Thread(
        target=start_foreground_monitor,
        daemon=True
    )

    monitor_thread.start()

    try:

        while True:

            history = (
                get_recent_foreground_activity()
            )

            if history:

                latest = history[0]

                print(
                    f"Process: "
                    f"{latest['process_name']}"
                )

                print(
                    f"Window: "
                    f"{latest['window_title']}"
                )

                print(
                    f"Last input: "
                    f"{latest['last_input_seconds']:.2f}s"
                )

                print(
                    f"History entries: "
                    f"{len(history)}"
                )

                print("-" * 50)

            time.sleep(1)

    except KeyboardInterrupt:

        print("\nStopped.")