import json

from memory.database.db import get_connection


def get_unprocessed_evidence():
    """
    Return activity evidence that has not yet been processed
    by Phase 4.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            ae.id,
            ae.source_type,
            ae.timestamp,
            ae.action,
            ae.duration_seconds,
            ae.details,
            ae.created_at
        FROM activity_evidence ae
        LEFT JOIN relevance_decisions rd
            ON ae.id = rd.evidence_id
        WHERE rd.evidence_id IS NULL
        ORDER BY ae.timestamp ASC
    """)

    rows = cursor.fetchall()
    connection.close()

    evidence = []

    for row in rows:
        evidence.append({
            "id": row[0],
            "source_type": row[1],
            "timestamp": row[2],
            "action": row[3],
            "duration_seconds": row[4],
            "details": json.loads(row[5]) if row[5] else {},
            "created_at": row[6]
        })

    return evidence