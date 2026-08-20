from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from memory.capture.activity_event import create_activity_event
from memory.capture.permissions import is_allowed
from memory.capture.deduplicator import ActivityDeduplicator
from memory.capture.pdf_capture import is_pdf, extract_pdf, save_activity


class FileActivityHandler(FileSystemEventHandler):

    def process_activity(self, activity):
        if deduplicator.is_duplicate(activity):
            return

        print(activity)

        # Only process PDFs that still exist
        if (
            is_pdf(activity["path"])
            and activity["action"] in ["created", "modified", "moved"]
            and Path(activity["path"]).exists()
        ):
            result = extract_pdf(activity["path"])
            save_activity(activity["path"], result)

            print("PDF extracted and saved to database.")

    def on_created(self, event):
        if event.is_directory:
            return

        if is_allowed(event.src_path):
            activity = create_activity_event(
                source_type="file",
                action="created",
                path=event.src_path
            )

            self.process_activity(activity)

    def on_modified(self, event):
        if event.is_directory:
            return

        if is_allowed(event.src_path):
            activity = create_activity_event(
                source_type="file",
                action="modified",
                path=event.src_path
            )

            self.process_activity(activity)

    def on_moved(self, event):
        if event.is_directory:
            return

        if is_allowed(event.dest_path):
            activity = create_activity_event(
                source_type="file",
                action="moved",
                path=event.dest_path,
                metadata={
                    "old_path": event.src_path
                }
            )

            self.process_activity(activity)

    def on_deleted(self, event):
        if event.is_directory:
            return

        if is_allowed(event.src_path):
            activity = create_activity_event(
                source_type="file",
                action="deleted",
                path=event.src_path
            )

            self.process_activity(activity)


if __name__ == "__main__":

    folder = Path("memory/tests/test_data").resolve()

    deduplicator = ActivityDeduplicator()
    event_handler = FileActivityHandler()

    observer = Observer()
    observer.schedule(
        event_handler,
        str(folder),
        recursive=True
    )

    observer.start()

    print(f"Monitoring: {folder}")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()

    observer.join()