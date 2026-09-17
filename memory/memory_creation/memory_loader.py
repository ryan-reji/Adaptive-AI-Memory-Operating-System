import json

from memory.database.db import get_connection


def get_memories():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            evidence_id,
            source_type,
            timestamp,
            action,
            duration_seconds,
            details,
            created_at,
            status
        FROM memory_records
        WHERE status = 'active'
        ORDER BY timestamp ASC
    """)

    rows = cursor.fetchall()
    connection.close()

    memories = []

    for row in rows:
        memories.append({
            "memory_id": row[0],
            "evidence_id": row[1],
            "source_type": row[2],
            "timestamp": row[3],
            "action": row[4],
            "duration_seconds": row[5],
            "details": json.loads(row[6]) if row[6] else {},
            "created_at": row[7],
            "status": row[8]
        })

    return memories


def get_unprocessed_memories():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            evidence_id,
            source_type,
            timestamp,
            action,
            duration_seconds,
            details,
            created_at,
            status
        FROM memory_records
        WHERE status = 'active'
        AND ai_processed = 0
        ORDER BY timestamp ASC
    """)

    rows = cursor.fetchall()
    connection.close()

    memories = []

    for row in rows:
        memories.append({
            "memory_id": row[0],
            "evidence_id": row[1],
            "source_type": row[2],
            "timestamp": row[3],
            "action": row[4],
            "duration_seconds": row[5],
            "details": json.loads(row[6]) if row[6] else {},
            "created_at": row[7],
            "status": row[8]
        })

    return memories