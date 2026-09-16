from memory.capture.common.activity_evidence import create_activity_evidence


def create_vscode_evidence(snapshot):
    """
    Convert a VS Code activity snapshot into common activity evidence.
    """

    return create_activity_evidence(
        source_type="vscode",
        timestamp=snapshot["last_seen"],
        action="editing",
        duration_seconds=snapshot["total_duration_seconds"],
        details={
            "editor": "Visual Studio Code",
            "project": snapshot["project"],
            "file": snapshot["file"],
            "sessions": snapshot["sessions"],
            "first_seen": snapshot["first_seen"],
            "last_seen": snapshot["last_seen"]
        }
    )


if __name__ == "__main__":

    test_snapshot = {
        "source_type": "vscode",
        "project": "Adaptive-AI-Memory-Operating-System",
        "file": "permissions.py",
        "total_duration_seconds": 1200,
        "sessions": 4,
        "first_seen": "2026-09-16T21:00:00",
        "last_seen": "2026-09-16T21:30:00"
    }

    evidence = create_vscode_evidence(test_snapshot)

    print("VS Code Activity Evidence:")
    print(evidence)