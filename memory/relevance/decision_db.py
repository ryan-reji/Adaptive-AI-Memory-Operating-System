from datetime import datetime

from memory.database.db import get_connection


VALID_DECISIONS = {"relevant", "irrelevant", "uncertain"}


def save_decision(evidence_id, decision):
    if decision not in VALID_DECISIONS:
        raise ValueError(f"Invalid decision: {decision}")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO relevance_decisions (
            evidence_id,
            decision,
            processed_at
        )
        VALUES (?, ?, ?)
    """, (
        evidence_id,
        decision,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()