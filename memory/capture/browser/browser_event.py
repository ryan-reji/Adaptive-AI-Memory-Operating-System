from datetime import datetime


def create_browser_event(activity):
    return {
        "source_type": "browser",
        "browser": activity["browser"],
        "title": activity["title"],
        "started_at": activity["started_at"],
        "ended_at": activity["ended_at"],
        "duration_seconds": activity["duration_seconds"],
        "captured_at": datetime.now().isoformat()
    }


if __name__ == "__main__":

    test_activity = {
        "browser": "Brave",
        "title": "GitHub - Adaptive-AI-Memory-Operating-System",
        "started_at": "2026-08-26T14:00:00",
        "ended_at": "2026-08-26T14:15:00",
        "duration_seconds": 900
    }

    event = create_browser_event(test_activity)

    print("Browser Event:")
    print(event)