import threading
import time

from memory.capture.file.file_monitor import start_file_monitor
from memory.capture.browser.browser_monitor import monitor_browser
from memory.capture.vscode.vscode_monitor import monitor
from memory.capture.foreground_activity import start_foreground_monitor


# =========================================================
# BROWSER MONITOR
# =========================================================

def start_browser_monitor():
    """
    Start the browser activity monitor.
    """

    monitor_browser()


# =========================================================
# VS CODE MONITOR
# =========================================================

def start_vscode_monitor():
    """
    Start the VS Code activity monitor.
    """

    monitor()


# =========================================================
# ALL MONITORS
# =========================================================

def start_all_monitors():
    """
    Start File, Browser and VS Code monitors concurrently.
    """

    # -----------------------------------------------------
    # Shared foreground activity monitor
    # -----------------------------------------------------

    foreground_thread = threading.Thread(
        target=start_foreground_monitor,
        daemon=True
    )

    foreground_thread.start()

    print("Foreground activity monitor started.")

    # -----------------------------------------------------
    # File monitor
    # -----------------------------------------------------

    file_thread = threading.Thread(
        target=start_file_monitor,
        kwargs={
            "start_foreground": False
        },
        daemon=True
    )

    # -----------------------------------------------------
    # Browser monitor
    # -----------------------------------------------------

    browser_thread = threading.Thread(
        target=start_browser_monitor,
        daemon=True
    )

    # -----------------------------------------------------
    # VS Code monitor
    # -----------------------------------------------------

    vscode_thread = threading.Thread(
        target=start_vscode_monitor,
        daemon=True
    )

    # -----------------------------------------------------
    # Start all monitors
    # -----------------------------------------------------

    file_thread.start()
    browser_thread.start()
    vscode_thread.start()

    print("\nAll activity monitors started.")
    print("Press Ctrl+C to stop.\n")

    # -----------------------------------------------------
    # Keep manager alive
    # -----------------------------------------------------

    try:

        while True:
            time.sleep(1)

    except KeyboardInterrupt:

        print("\nActivity manager stopped.")


# =========================================================
# STANDALONE
# =========================================================

if __name__ == "__main__":
    start_all_monitors()