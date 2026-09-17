import json

from memory.database.db import get_connection


def save_activity_evidence(evidence):
    """
    Save common activity evidence to SQLite.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO activity_evidence (
            source_type,
            timestamp,
            action,
            duration_seconds,
            details,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        evidence["source_type"],
        evidence["timestamp"],
        evidence["action"],
        evidence["duration_seconds"],
        json.dumps(evidence["details"]),
        evidence["created_at"]
    ))

    connection.commit()

    evidence_id = cursor.lastrowid

    connection.close()

    return evidence_id

if __name__ == "__main__":

    test_evidence = {
        "source_type": "browser",
        "timestamp": "2026-09-17T11:30:00",
        "action": "viewed",
        "duration_seconds": 120,
        "details": {
            "browser": "Brave",
            "title": "GitHub",
            "sessions": 2
        },
        "created_at": "2026-09-17T11:30:00"
    }

    evidence_id = save_activity_evidence(test_evidence)

    print("Evidence saved successfully.")
    print("Evidence ID:", evidence_id)