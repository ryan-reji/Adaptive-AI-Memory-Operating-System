def create_browser_snapshot(aggregated_activity):
    return {
        "source_type": "browser",
        "browser": aggregated_activity["browser"],
        "title": aggregated_activity["title"],
        "total_duration_seconds": aggregated_activity[
            "total_duration_seconds"
        ],
        "sessions": aggregated_activity["sessions"],
        "first_seen": aggregated_activity["first_seen"],
        "last_seen": aggregated_activity["last_seen"]
    }


if __name__ == "__main__":

    test_activity = {
        "browser": "Brave",
        "title": "GitHub - Adaptive-AI-Memory-Operating-System",
        "total_duration_seconds": 1800,
        "sessions": 3,
        "first_seen": "2026-08-26T14:00:00",
        "last_seen": "2026-08-26T14:30:00"
    }

    snapshot = create_browser_snapshot(test_activity)

    print("Browser Snapshot:")
    print(snapshot)