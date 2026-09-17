import threading
import time

from memory.capture.file.file_monitor import FileActivityHandler
from memory.capture.browser.browser_monitor import monitor_browser
from memory.capture.vscode.vscode_monitor import monitor


def start_file_monitor():
    """
    Start the file activity monitor.
    """

    from watchdog.observers import Observer
    from pathlib import Path

    folder = Path("memory/tests/test_data").resolve()

    observer = Observer()
    event_handler = FileActivityHandler()

    observer.schedule(
        event_handler,
        str(folder),
        recursive=True
    )

    observer.start()

    print(f"File monitor started: {folder}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


def start_browser_monitor():
    """
    Start the browser activity monitor.
    """

    monitor_browser()


def start_vscode_monitor():
    """
    Start the VS Code activity monitor.
    """

    monitor()


def start_all_monitors():
    """
    Start File, Browser and VS Code monitors concurrently.
    """

    file_thread = threading.Thread(
        target=start_file_monitor,
        daemon=True
    )

    browser_thread = threading.Thread(
        target=start_browser_monitor,
        daemon=True
    )

    vscode_thread = threading.Thread(
        target=start_vscode_monitor,
        daemon=True
    )

    file_thread.start()
    browser_thread.start()
    vscode_thread.start()

    print("\nAll activity monitors started.")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nActivity manager stopped.")


if __name__ == "__main__":
    start_all_monitors()