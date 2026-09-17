from memory.database.db import get_connection
from memory.memory_creation.memory_writer import create_memory


def get_retained_evidence():
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
        JOIN relevance_decisions rd
            ON ae.id = rd.evidence_id
        WHERE rd.decision IN ('relevant', 'uncertain')
        AND NOT EXISTS (
            SELECT 1
            FROM memory_records mr
            WHERE mr.evidence_id = ae.id
        )
        ORDER BY ae.timestamp ASC
    """)

    rows = cursor.fetchall()
    connection.close()

    import json

    return [
        {
            "id": row[0],
            "source_type": row[1],
            "timestamp": row[2],
            "action": row[3],
            "duration_seconds": row[4],
            "details": json.loads(row[5]) if row[5] else {},
            "created_at": row[6]
        }
        for row in rows
    ]


def process_retained_evidence():
    evidence = get_retained_evidence()

    if not evidence:
        print("No retained evidence to convert into memories.")
        return

    created = 0

    for item in evidence:
        memory_id = create_memory(item)

        if memory_id:
            created += 1

    print(f"Created {created} memory records.")


if __name__ == "__main__":
    process_retained_evidence()