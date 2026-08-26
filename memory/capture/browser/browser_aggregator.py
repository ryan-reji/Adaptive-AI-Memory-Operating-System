from collections import defaultdict


def create_activity_key(event):
    browser = event["browser"].strip().lower()
    title = event["title"].strip().lower()

    return f"{browser}:{title}"


def aggregate_browser_events(events):
    aggregated = defaultdict(lambda: {
        "browser": None,
        "title": None,
        "total_duration_seconds": 0,
        "sessions": 0,
        "first_seen": None,
        "last_seen": None
    })

    for event in events:

        key = create_activity_key(event)

        activity = aggregated[key]

        activity["browser"] = event["browser"]
        activity["title"] = event["title"]

        activity["total_duration_seconds"] += (
            event["duration_seconds"]
        )

        activity["sessions"] += 1

        if (
            activity["first_seen"] is None
            or event["started_at"] < activity["first_seen"]
        ):
            activity["first_seen"] = event["started_at"]

        if (
            activity["last_seen"] is None
            or event["ended_at"] > activity["last_seen"]
        ):
            activity["last_seen"] = event["ended_at"]

    return list(aggregated.values())


if __name__ == "__main__":

    test_events = [
        {
            "browser": "Brave",
            "title": "GitHub - Project",
            "started_at": "2026-08-26T10:00:00",
            "ended_at": "2026-08-26T10:08:00",
            "duration_seconds": 480
        },
        {
            "browser": "Brave",
            "title": "YouTube",
            "started_at": "2026-08-26T10:08:00",
            "ended_at": "2026-08-26T10:13:00",
            "duration_seconds": 300
        },
        {
            "browser": "Brave",
            "title": "GitHub - Project",
            "started_at": "2026-08-26T10:13:00",
            "ended_at": "2026-08-26T10:25:00",
            "duration_seconds": 720
        }
    ]

    result = aggregate_browser_events(test_events)

    print("Aggregated Browser Activity:")

    for activity in result:
        print(activity)