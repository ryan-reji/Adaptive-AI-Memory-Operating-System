import json
from json import JSONDecodeError

from memory.database.db import get_connection


SENSITIVE_DETAIL_KEYS = {
    "content",
    "path",
    "source_path",
    "old_path",
    "raw",
}


def _sanitize_details(value):
    """
    Recursively remove sensitive or internal fields before
    memory data is returned through the API.
    """

    if isinstance(value, dict):
        sanitized = {}

        for key, item in value.items():
            normalized_key = str(key).lower()

            if (
                normalized_key in SENSITIVE_DETAIL_KEYS
                or normalized_key.endswith("_path")
            ):
                continue

            sanitized[key] = _sanitize_details(item)

        return sanitized

    if isinstance(value, list):
        return [_sanitize_details(item) for item in value]

    return value


def _row_to_memory(row):
    raw_details = row[6]

    if raw_details:
        try:
            details = json.loads(raw_details)
        except JSONDecodeError:
            details = {}
    else:
        details = {}

    return {
        "id": row[0],
        "evidence_id": row[1],
        "source_type": row[2],
        "timestamp": row[3],
        "action": row[4],
        "duration_seconds": row[5],
        "details": _sanitize_details(details),
        "created_at": row[7],
        "status": row[8],
        "ai_processed": bool(row[9]),
    }


def get_memories(limit=50, offset=0):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            evidence_id,
            source_type,
            timestamp,
            action,
            duration_seconds,
            details,
            created_at,
            status,
            ai_processed
        FROM memory_records
        WHERE status = 'active'
        ORDER BY timestamp DESC
        LIMIT ? OFFSET ?
        """,
        (limit, offset),
    )

    rows = cursor.fetchall()
    connection.close()

    return [_row_to_memory(row) for row in rows]


def get_memory(memory_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            evidence_id,
            source_type,
            timestamp,
            action,
            duration_seconds,
            details,
            created_at,
            status,
            ai_processed
        FROM memory_records
        WHERE id = ?
          AND status = 'active'
        """,
        (memory_id,),
    )

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None

    return _row_to_memory(row)