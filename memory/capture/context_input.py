from memory.database.db import get_connection
from memory.capture.activity_snapshot import create_snapshot


def get_recent_activities(limit=5):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT source_type, source_path, title, content, captured_at
        FROM activities
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    connection.close()

    activities = []

    for row in rows:
        activities.append({
            "source_type": row[0],
            "source_path": row[1],
            "title": row[2],
            "content": row[3],
            "captured_at": row[4]
        })

    return activities


if __name__ == "__main__":
    activities = get_recent_activities()

    for activity in activities:
        snapshot = create_snapshot(activity)
        print(snapshot)