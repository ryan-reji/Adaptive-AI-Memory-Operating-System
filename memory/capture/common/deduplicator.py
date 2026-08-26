import time


class ActivityDeduplicator:

    def __init__(self, window_seconds=5):
        self.window_seconds = window_seconds
        self.last_events = {}

    def is_duplicate(self, event):
        key = (
            event["source_type"],
            event["action"],
            event["path"]
        )

        current_time = time.time()

        if key in self.last_events:
            previous_time = self.last_events[key]

            if current_time - previous_time < self.window_seconds:
                return True

        self.last_events[key] = current_time

        return False