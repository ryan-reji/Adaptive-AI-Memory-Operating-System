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
    get_permission_mode
)
from memory.capture.common.deduplicator import ActivityDeduplicator

from memory.capture.foreground_activity import (
    get_recent_foreground_activity,
    start_foreground_monitor
)

from memory.capture.user_interaction_filter import (
    is_user_interacting_with_file
)

from memory.capture.file.universal_extractor import get_chunk
from memory.capture.file.file_snapshot import create_snapshot
from memory.capture.file.file_evidence import create_file_evidence
from memory.database.activity_evidence_db import save_activity_evidence


class FileActivityHandler(FileSystemEventHandler):

    def __init__(self):
        super().__init__()
        self.deduplicator = ActivityDeduplicator()

    def process_activity(self, activity, event_timestamp=None):
        """
        Process a filesystem activity event.
        """

        if self.deduplicator.is_duplicate(activity):
            return

        # -------------------------------------------------
        # Permission check
        # -------------------------------------------------

        if not is_allowed(activity["path"]):
            print(
                "Ignoring file outside allowed permissions:",
                activity["path"]
            )
            return

        # -------------------------------------------------
        # Exact filesystem event timestamp
        # -------------------------------------------------

        if event_timestamp is None:
            try:
                event_timestamp = datetime.fromisoformat(
                    activity["timestamp"]
                ).timestamp()
            except Exception:
                event_timestamp = time.time()

        # -------------------------------------------------
        # Foreground activity correlation
        # -------------------------------------------------

        foreground_history = get_recent_foreground_activity()

        if not is_user_interacting_with_file(
            activity["path"],
            foreground_history,
            event_timestamp
        ):
            print(
                "Ignoring background file activity:",
                activity["path"]
            )
            return

        # -------------------------------------------------
        # User-driven activity detected
        # -------------------------------------------------

        print("\nUser-driven file activity detected:")
        print(activity)

        # Deleted files cannot be extracted.
        if activity["action"] == "deleted":
            return

        file_path = Path(activity["path"])

        if not file_path.exists():
            return

        # -------------------------------------------------
        # Extract content
        # -------------------------------------------------

        result = get_chunk(
            activity["path"],
            chunk_number=0
        )

        # -------------------------------------------------
        # Create snapshot
        # -------------------------------------------------

        snapshot = create_snapshot(
            activity,
            result
        )

        print("Activity Snapshot:")
        print(snapshot)

        # -------------------------------------------------
        # Create evidence
        # -------------------------------------------------

        evidence = create_file_evidence(snapshot)

        print("Activity Evidence:")
        print(evidence)

        # -------------------------------------------------
        # Save evidence
        # -------------------------------------------------

        evidence_id = save_activity_evidence(evidence)

        print("Saved Evidence ID:", evidence_id)

    # =====================================================
    # CREATED
    # =====================================================

    def on_created(self, event):

        if event.is_directory:
            return

        event_timestamp = time.time()

        if is_allowed(event.src_path):

            activity = create_activity_event(
                source_type="file",
                action="created",
                path=event.src_path
            )

            self.process_activity(
                activity,
                event_timestamp
            )

    # =====================================================
    # MODIFIED
    # =====================================================

    def on_modified(self, event):

        if event.is_directory:
            return

        event_timestamp = time.time()

        if is_allowed(event.src_path):

            activity = create_activity_event(
                source_type="file",
                action="modified",
                path=event.src_path
            )

            self.process_activity(
                activity,
                event_timestamp
            )

    # =====================================================
    # MOVED
    # =====================================================

    def on_moved(self, event):

        if event.is_directory:
            return

        event_timestamp = time.time()

        if is_allowed(event.dest_path):

            activity = create_activity_event(
                source_type="file",
                action="moved",
                path=event.dest_path,
                metadata={
                    "old_path": event.src_path
                }
            )

            self.process_activity(
                activity,
                event_timestamp
            )

    # =====================================================
    # DELETED
    # =====================================================

    def on_deleted(self, event):

        if event.is_directory:
            return

        event_timestamp = time.time()

        if is_allowed(event.src_path):

            activity = create_activity_event(
                source_type="file",
                action="deleted",
                path=event.src_path
            )

            self.process_activity(
                activity,
                event_timestamp
            )


# =========================================================
# MONITORING SCOPE
# =========================================================

def get_monitoring_folder():
    """
    Determine the Watchdog monitoring scope.

    allow_all:
        C:\\Users\\<username>

    allow_only:
        memory\\tests\\test_data
    """

    permission_mode = get_permission_mode()

    if permission_mode == "allow_all":

        username = os.environ.get("USERNAME", "")

        if not username:
            raise RuntimeError(
                "Could not determine Windows username."
            )

        return Path(
            os.path.join(
                r"C:\Users",
                username
            )
        ).resolve()

    if permission_mode == "allow_only":

        return Path(
            "memory/tests/test_data"
        ).resolve()

    raise RuntimeError(
        f"Unsupported permission mode: {permission_mode}"
    )


# =========================================================
# START FILE MONITOR
# =========================================================

def start_file_monitor(start_foreground=True):
    """
    Start the filesystem monitor.

    The monitoring scope is determined here.

    start_foreground=True:
        Used when running this module directly.

    start_foreground=False:
        Used by activity_manager, which already owns
        the shared foreground monitor.
    """

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
        recursive=True
    )

    # -----------------------------------------------------
    # Foreground monitor
    # -----------------------------------------------------

    if start_foreground:

        foreground_thread = threading.Thread(
            target=start_foreground_monitor,
            daemon=True
        )

        foreground_thread.start()

        print("Foreground activity monitor started.")

    # -----------------------------------------------------
    # Watchdog
    # -----------------------------------------------------

    observer.start()

    print("\nFile monitor started.")
    print(f"Permission mode: {permission_mode}")
    print(f"Monitoring: {folder}")
    print("Press Ctrl+C to stop.\n")

    try:

        while True:
            time.sleep(1)

    except KeyboardInterrupt:

        print("\nStopping file monitor...")
        observer.stop()

    observer.join()


# =========================================================
# STANDALONE
# =========================================================

if __name__ == "__main__":
    start_file_monitor()