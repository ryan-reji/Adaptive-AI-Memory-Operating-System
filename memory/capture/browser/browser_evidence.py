from memory.capture.common.activity_evidence import create_activity_evidence


def create_browser_evidence(snapshot):
    """
    Convert a browser activity snapshot into common activity evidence.
    """

    return create_activity_evidence(
        source_type="browser",
        timestamp=snapshot["last_seen"],
        action="viewed",
        duration_seconds=snapshot["total_duration_seconds"],
        details={
            "browser": snapshot["browser"],
            "title": snapshot["title"],
            "sessions": snapshot["sessions"],
            "first_seen": snapshot["first_seen"],
            "last_seen": snapshot["last_seen"]
        }
    )


if __name__ == "__main__":

    test_snapshot = {
        "source_type": "browser",
        "browser": "Brave",
        "title": "GitHub - Adaptive-AI-Memory-Operating-System",
        "total_duration_seconds": 1800,
        "sessions": 3,
        "first_seen": "2026-08-26T14:00:00",
        "last_seen": "2026-08-26T14:30:00"
    }

    evidence = create_browser_evidence(test_snapshot)

    print("Browser Activity Evidence:")
    print(evidence)