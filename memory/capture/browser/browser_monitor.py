import time
from datetime import datetime

import win32gui
import win32process
import psutil

from memory.capture.browser.browser_permissions import (
    is_browser_allowed,
    is_private_capture_allowed
)


SUPPORTED_BROWSERS = {
    "chrome.exe": "Chrome",
    "brave.exe": "Brave",
    "msedge.exe": "Edge",
    "firefox.exe": "Firefox"
}


def get_active_window():
    hwnd = win32gui.GetForegroundWindow()

    if not hwnd:
        return None

    title = win32gui.GetWindowText(hwnd)

    if not title:
        return None

    try:
        _, process_id = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(process_id)

        executable = process.name().lower()

    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

    browser = SUPPORTED_BROWSERS.get(executable)

    if browser is None:
        return None

    return {
        "browser": browser,
        "title": title,
        "window_handle": hwnd,
        "timestamp": datetime.now().isoformat()
    }


def monitor_browser(interval=1):
    previous_activity = None
    start_time = None

    print("Browser monitor started.")
    print("Press Ctrl+C to stop.")

    try:
        while True:

            current_activity = get_active_window()

            # No supported browser currently active
            if current_activity is None:
                if previous_activity is not None:
                    finish_activity(
                        previous_activity,
                        start_time
                    )

                    previous_activity = None
                    start_time = None

                time.sleep(interval)
                continue

            # Check browser permission
            browser = current_activity["browser"]

            if not is_browser_allowed(browser):
                current_activity = None

                if previous_activity is not None:
                    finish_activity(
                        previous_activity,
                        start_time
                    )

                    previous_activity = None
                    start_time = None

                time.sleep(interval)
                continue

            # First allowed browser activity
            if previous_activity is None:

                previous_activity = current_activity
                start_time = time.time()

            # Browser/window title changed
            elif (
                current_activity["browser"]
                != previous_activity["browser"]
                or current_activity["title"]
                != previous_activity["title"]
            ):

                finish_activity(
                    previous_activity,
                    start_time
                )

                previous_activity = current_activity
                start_time = time.time()

            time.sleep(interval)

    except KeyboardInterrupt:

        if previous_activity is not None:
            finish_activity(
                previous_activity,
                start_time
            )

        print("\nBrowser monitor stopped.")


def finish_activity(activity, start_time):
    duration = time.time() - start_time

    print({
        "browser": activity["browser"],
        "title": activity["title"],
        "started_at": datetime.fromtimestamp(
            start_time
        ).isoformat(),
        "ended_at": datetime.now().isoformat(),
        "duration_seconds": round(duration, 2)
    })


if __name__ == "__main__":
    monitor_browser()