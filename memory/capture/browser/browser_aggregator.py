from memory.database.db import get_connection


def create_activity_key(event):
    browser = event["browser"].strip().lower()
    title = event["title"].strip().lower()

    return f"{browser}:{title}"


def aggregate_browser_event(event):
    activity_key = create_activity_key(event)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            total_duration_seconds,
            session_count,
            first_seen,
            last_seen
        FROM browser_activity
        WHERE activity_key = ?
    """, (activity_key,))

    row = cursor.fetchone()

    if row is None:
        cursor.execute("""
            INSERT INTO browser_activity (
                activity_key,
                browser,
                title,
                total_duration_seconds,
                session_count,
                first_seen,
                last_seen
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            activity_key,
            event["browser"],
            event["title"],
            event["duration_seconds"],
            1,
            event["started_at"],
            event["ended_at"]
        ))

    else:
        activity_id = row[0]
        current_duration = row[1]
        current_sessions = row[2]
        first_seen = row[3]
        last_seen = row[4]

        new_duration = (
            current_duration +
            event["duration_seconds"]
        )

        new_sessions = current_sessions + 1

        new_first_seen = min(
            first_seen,
            event["started_at"]
        )

        new_last_seen = max(
            last_seen,
            event["ended_at"]
        )

        cursor.execute("""
            UPDATE browser_activity
            SET
                total_duration_seconds = ?,
                session_count = ?,
                first_seen = ?,
                last_seen = ?
            WHERE id = ?
        """, (
            new_duration,
            new_sessions,
            new_first_seen,
            new_last_seen,
            activity_id
        ))

    connection.commit()

    cursor.execute("""
        SELECT
            browser,
            title,
            total_duration_seconds,
            session_count,
            first_seen,
            last_seen
        FROM browser_activity
        WHERE activity_key = ?
    """, (activity_key,))

    result = cursor.fetchone()

    connection.close()

    return {
        "browser": result[0],
        "title": result[1],
        "total_duration_seconds": result[2],
        "sessions": result[3],
        "first_seen": result[4],
        "last_seen": result[5]
    }