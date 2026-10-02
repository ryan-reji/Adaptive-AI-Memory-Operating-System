import time
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from memory.capture.foreground_activity import get_foreground_activity
from memory.capture.user_interaction_filter import (
    is_user_interacting_with_file
)


WATCH_FOLDER = Path("memory/tests/test_data").resolve()


class TestHandler(FileSystemEventHandler):

    def report(self, action, path):

        activity = get_foreground_activity()

        print("\n" + "=" * 60)
        print(f"FILE EVENT          : {action}")
        print(f"FILE                : {path}")

        if activity:

            print(
                f"FOREGROUND PID      : "
                f"{activity['process_id']}"
            )

            print(
                f"WINDOW              : "
                f"{activity['window_title']}"
            )

            print(
                f"LAST INPUT          : "
                f"{activity['last_input_seconds']:.2f}s ago"
            )

            user_interaction = is_user_interacting_with_file(
                path,
                activity
            )

            print(
                f"USER INTERACTION    : "
                f"{'YES' if user_interaction else 'NO'}"
            )

        else:
            print("FOREGROUND          : None")
            print("USER INTERACTION    : NO")

        print("=" * 60)

    def on_created(self, event):

        if not event.is_directory:
            self.report(
                "CREATED",
                event.src_path
            )

    def on_modified(self, event):

        if not event.is_directory:
            self.report(
                "MODIFIED",
                event.src_path
            )

    def on_deleted(self, event):

        if not event.is_directory:
            self.report(
                "DELETED",
                event.src_path
            )

    def on_moved(self, event):

        if not event.is_directory:
            self.report(
                "MOVED",
                event.dest_path
            )


if __name__ == "__main__":

    print(f"Monitoring: {WATCH_FOLDER}")
    print("Perform file activity in this folder.")
    print("Press Ctrl+C to stop.\n")

    observer = Observer()

    observer.schedule(
        TestHandler(),
        str(WATCH_FOLDER),
        recursive=True
    )

    observer.start()

    try:

        while True:
            time.sleep(1)

    except KeyboardInterrupt:

        observer.stop()

    observer.join()