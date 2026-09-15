def create_vscode_snapshot(aggregated_activity):
    """
    Create a compact VS Code activity snapshot
    from aggregated activity.
    """

    return {
        "source_type": "vscode",
        "project": aggregated_activity["project"],
        "file": aggregated_activity["file"],
        "total_duration_seconds": aggregated_activity["total_duration_seconds"],
        "sessions": aggregated_activity["sessions"],
        "first_seen": aggregated_activity["first_seen"],
        "last_seen": aggregated_activity["last_seen"]
    }