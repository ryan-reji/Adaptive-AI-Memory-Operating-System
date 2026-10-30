
import json

from memory.database.db import get_connection


def create_memory(evidence):
    connection = get_connection()
    cursor = connection.cursor()

    try:
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

        # Return an ID only if a new record was inserted.
        if cursor.rowcount == 0:
            return None

        return cursor.lastrowid

    finally:
        connection.close()