from memory.database.db import get_connection


def create_snapshot(activity):
    return {
        "source_type": activity["source_type"],
        "source_path": activity["source_path"],
        "title": activity["title"],
        "text_preview": activity["content"][:1000],
        "captured_at": activity["captured_at"]
    }


def get_latest_activity():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT source_type, source_path, title, content, captured_at
        FROM activities
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None

    return {
        "source_type": row[0],
        "source_path": row[1],
        "title": row[2],
        "content": row[3],
        "captured_at": row[4]
    }


if __name__ == "__main__":
    activity = get_latest_activity()

    if activity:
        snapshot = create_snapshot(activity)

        print("Activity Snapshot:")
        print(snapshot)
    else:
        print("No activities found.")