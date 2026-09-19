import json
from json import JSONDecodeError

from backend.app.services.privacy_service import sanitize_details
from memory.database.db import get_connection


def _row_to_evidence(row):
    raw_details = row[5]

    if raw_details:
        try:
            details = json.loads(raw_details)
        except JSONDecodeError:
            details = {}
    else:
        details = {}

    return {
        "id": row[0],
        "source_type": row[1],
        "timestamp": row[2],
        "action": row[3],
        "duration_seconds": row[4],
        "details": sanitize_details(details),
        "created_at": row[6],
    }


def get_evidence(limit=50, offset=0):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            source_type,
            timestamp,
            action,
            duration_seconds,
            details,
            created_at
        FROM activity_evidence
        ORDER BY timestamp DESC, id DESC
        LIMIT ? OFFSET ?
        """,
        (limit, offset),
    )

    rows = cursor.fetchall()
    connection.close()

    return [_row_to_evidence(row) for row in rows]


def get_evidence_by_id(evidence_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            source_type,
            timestamp,
            action,
            duration_seconds,
            details,
            created_at
        FROM activity_evidence
        WHERE id = ?
        """,
        (evidence_id,),
    )

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None

    return _row_to_evidence(row)