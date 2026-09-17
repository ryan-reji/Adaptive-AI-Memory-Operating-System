from datetime import datetime


def create_activity_evidence(
    source_type,
    timestamp,
    action=None,
    duration_seconds=None,
    details=None
):
    """
    Create a common activity-evidence structure.

    Common fields are kept consistent across all activity sources,
    while source-specific information is stored in details.
    """

    return {
        "source_type": source_type,
        "timestamp": timestamp,
        "action": action,
        "duration_seconds": duration_seconds,
        "details": details or {},
        "created_at": datetime.now().isoformat()
    }


if __name__ == "__main__":

    evidence = create_activity_evidence(
        source_type="browser",
        timestamp="2026-08-26T14:00:00",
        action="viewed",
        duration_seconds=300,
        details={
            "browser": "Brave",
            "title": "GitHub",
            "private": False
        }
    )

    print("Activity Evidence:")
    print(evidence)