import json

from memory.database.db import get_connection


def create_memory(evidence):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO memory_records (
            evidence_id,
            source_type,
            timestamp,
            action,
            duration_seconds,
            details,
            created_at,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        evidence["id"],
        evidence["source_type"],
        evidence["timestamp"],
        evidence["action"],
        evidence["duration_seconds"],
        json.dumps(evidence["details"]),
        evidence["created_at"],
        "active"
    ))

    connection.commit()
    memory_id = cursor.lastrowid
    connection.close()

    return memory_id