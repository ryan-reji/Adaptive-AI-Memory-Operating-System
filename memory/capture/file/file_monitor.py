
from pathlib import Path
import os
import threading
import time
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from memory.capture.common.activity_event import create_activity_event
from memory.capture.common.permissions import (
    is_allowed,
    get_permission_mode,
)
from memory.capture.common.deduplicator import ActivityDeduplicator
from memory.capture.foreground_activity import (
    get_recent_foreground_activity,
    start_foreground_monitor,
)
from memory.capture.user_interaction_filter import (
    is_user_interacting_with_file,
)
from memory.capture.file.universal_extractor import get_chunk
from memory.capture.file.file_snapshot import create_snapshot
from memory.capture.file.file_evidence import create_file_evidence
from memory.database.activity_evidence_db import save_activity_evidence


# Allow correlation with recent foreground samples.
VSCODE_MAX_TIME_DIFFERENCE = 5.0


def is_vscode_file_activity(
    file_path,
    foreground_history,
    event_timestamp=None,
):
    """
    Match a filesystem event against a recent VS Code
    foreground window containing the same filename.
    """

    if not foreground_history:
        return False

    filename = Path(file_path).name.casefold()

    if not filename:
        return False

    closest_match = None
    smallest_difference = float("inf")

    for activity in foreground_history:

        process_name = (
            activity.get("process_name") or ""
        ).casefold()

        if process_name not in {
            "code.exe",
            "code-insiders.exe",
        }:
            continue

        title = (
            activity.get("window_title") or ""
        ).casefold()

        # The active VS Code title must contain this filename.
        if filename not in title:
            continue

        timestamp = activity.get("timestamp")

        if event_timestamp is not None and timestamp is not None:
            try:
                difference = abs(
                    float(event_timestamp) - float(timestamp)
                )
            except (TypeError, ValueError):
                continue
        else:
            difference = 0.0

        if difference < smallest_difference:
            smallest_difference = difference
            closest_match = activity

    if closest_match is None:
        return False

    if smallest_difference > VSCODE_MAX_TIME_DIFFERENCE:
        return False

    return True


class FileActivityHandler(FileSystemEventHandler):

    def __init__(self):
        super().__init__()
        self.deduplicator = ActivityDeduplicator()

    def process_activity(
        self,
        activity,
        event_timestamp=None,
    ):
        """Process a filesystem activity event."""

        if self.deduplicator.is_duplicate(activity):
            return

        path = activity.get("path")

        if not path:
            return

        if not is_allowed(path):
            return

        if event_timestamp is None:
            try:
                event_timestamp = datetime.fromisoformat(
                    activity["timestamp"]
                ).timestamp()
            except Exception:
                event_timestamp = time.time()

        foreground_history = get_recent_foreground_activity()

        normal_interaction = is_user_interacting_with_file(
            path,
            foreground_history,
            event_timestamp,
        )

        vscode_interaction = False

        if not normal_interaction:
            vscode_interaction = is_vscode_file_activity(
                path,
                foreground_history,
                event_timestamp,
            )

        if not normal_interaction and not vscode_interaction:
            return

        if vscode_interaction:
            print("\nVS Code file activity detected:")
        else:
            print("\nUser-driven file activity detected:")

        print("Action:", activity.get("action"))
        print("Full path:", Path(path).resolve())

        if activity.get("action") == "deleted":
            return

        file_path = Path(path)

        if not file_path.is_file():
            return

        try:
            result = get_chunk(
                str(file_path),
                chunk_number=0,
            )

            snapshot = create_snapshot(
                activity,
                result,
            )

            evidence = create_file_evidence(snapshot)

            evidence_id = save_activity_evidence(evidence)

            print("Saved file evidence ID:", evidence_id)
            print("Captured full path:", str(file_path.resolve()))

        except Exception as exc:
            print(
                f"File evidence processing error for "
                f"{file_path}: {exc}"
            )

    def on_created(self, event):

        if event.is_directory:
            return

        event_timestamp = time.time()

        if not is_allowed(event.src_path):
            return

        activity = create_activity_event(
            source_type="file",
            action="created",
            path=event.src_path,
        )

        self.process_activity(
            activity,
            event_timestamp,
        )

    def on_modified(self, event):

        if event.is_directory:
            return

        event_timestamp = time.time()

        if not is_allowed(event.src_path):
            return

        activity = create_activity_event(
            source_type="file",
            action="modified",
            path=event.src_path,
        )

        self.process_activity(
            activity,
            event_timestamp,
        )

    def on_moved(self, event):

        if event.is_directory:
            return

        event_timestamp = time.time()

        if not is_allowed(event.dest_path):
            return

        activity = create_activity_event(
            source_type="file",
            action="moved",
            path=event.dest_path,
            metadata={
                "old_path": event.src_path,
            },
        )

        self.process_activity(
            activity,
            event_timestamp,
        )

    def on_deleted(self, event):

        if event.is_directory:
            return

        event_timestamp = time.time()

        if not is_allowed(event.src_path):
            return

        activity = create_activity_event(
            source_type="file",
            action="deleted",
            path=event.src_path,
        )

        self.process_activity(
            activity,
            event_timestamp,
        )


def get_monitoring_folder():

    permission_mode = get_permission_mode()

    if permission_mode == "allow_all":

        username = os.environ.get("USERNAME", "")

        if not username:
            raise RuntimeError(
                "Could not determine Windows username."
            )

        return Path(
            os.path.join(r"C:\Users", username)
        ).resolve()

    if permission_mode == "allow_only":
        return Path(
            "memory/tests/test_data"
        ).resolve()

    raise RuntimeError(
        f"Unsupported permission mode: {permission_mode}"
    )


def start_file_monitor(start_foreground=True):

    folder = get_monitoring_folder()
    permission_mode = get_permission_mode()

    if not folder.exists():
        raise RuntimeError(
            f"Monitoring folder does not exist: {folder}"
        )

    event_handler = FileActivityHandler()
    observer = Observer()

    observer.schedule(
        event_handler,
        str(folder),
        recursive=True,
    )

    if start_foreground:

        foreground_thread = threading.Thread(
            target=start_foreground_monitor,
            daemon=True,
        )

        foreground_thread.start()

        print("Foreground activity monitor started.")

    observer.start()

    print("\nFile monitor started.")
    print("Permission mode:", permission_mode)
    print("Monitoring:", folder)
    print("VS Code path correlation enabled.")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping file monitor...")
        observer.stop()
        observer.join()


if __name__ == "__main__":
    start_file_monitor()
