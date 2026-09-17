import json
from datetime import datetime
from pathlib import Path

from memory.database.db import get_connection


JSON_PATH = Path("memory/data/memories.json")


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
        ORDER BY id ASC
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


def load_json():
    if not JSON_PATH.exists():
        return {
            "date": datetime.now().date().isoformat(),
            "memories": []
        }

    with open(JSON_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(data):
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(JSON_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def update_daily_json():
    today = datetime.now().date().isoformat()

    data = load_json()

    # Start a fresh JSON file when the day changes
    if data.get("date") != today:
        data = {
            "date": today,
            "memories": []
        }

    existing_ids = {
        memory["memory_id"]
        for memory in data["memories"]
    }

    new_memories = get_unprocessed_memories()

    added_memories = []

    for memory in new_memories:
        if memory["memory_id"] not in existing_ids:
            data["memories"].append(memory)
            added_memories.append(memory)

    save_json(data)

    return added_memories


def mark_processed(memory_ids):
    if not memory_ids:
        return

    connection = get_connection()
    cursor = connection.cursor()

    placeholders = ",".join("?" for _ in memory_ids)

    cursor.execute(
        f"""
        UPDATE memory_records
        SET ai_processed = 1
        WHERE id IN ({placeholders})
        """,
        memory_ids
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":
    added = update_daily_json()

    print(f"Added {len(added)} new memories to JSON.")

    for memory in added:
        print(f"Memory ID: {memory['memory_id']}")