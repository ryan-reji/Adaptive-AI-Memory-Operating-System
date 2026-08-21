from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from memory.capture.activity_event import create_activity_event
from memory.capture.permissions import is_allowed
from memory.capture.deduplicator import ActivityDeduplicator
from memory.capture.universal_extractor import extract_file


class FileActivityHandler(FileSystemEventHandler):

    def process_activity(self, activity):
     if deduplicator.is_duplicate(activity):
        return

     print(activity)

    # Deleted files are not sent for extraction
     if activity["action"] == "deleted":
        return

     file_path = Path(activity["path"])

     if not file_path.exists():
        return

     result = extract_file(activity["path"])

     print("Extraction level:", result["extraction_level"])
     print("Metadata:", result["metadata"])

     if result["content"]:
        print("Content preview:")
        print(result["content"][:500])

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