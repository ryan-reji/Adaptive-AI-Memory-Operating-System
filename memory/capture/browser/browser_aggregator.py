from memory.database.db import get_connection


def create_activity_key(event):
    browser = event["browser"].strip().lower()
    title = event["title"].strip().lower()

    return f"{browser}:{title}"


def aggregate_browser_event(event):
    """
    Add a browser event to:
    1. The persistent lifetime activity aggregate.
    2. The daily activity history.
    """

    activity_key = create_activity_key(event)

    connection = get_connection()
    cursor = connection.cursor()

    # 1. Find existing lifetime activity
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

        activity_id = cursor.lastrowid

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

    # 2. Determine activity date
    activity_date = event["started_at"][:10]

    # 3. Find daily activity for this activity + date
    cursor.execute("""
        SELECT id
        FROM browser_daily_activity
        WHERE activity_id = ?
          AND activity_date = ?
    """, (
        activity_id,
        activity_date
    ))

    daily_row = cursor.fetchone()

    if daily_row is None:
        cursor.execute("""
            INSERT INTO browser_daily_activity (
                activity_id,
                activity_date,
                first_seen,
                last_seen,
                duration_seconds
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            activity_id,
            activity_date,
            event["started_at"],
            event["ended_at"],
            event["duration_seconds"]
        ))

    else:
        cursor.execute("""
            UPDATE browser_daily_activity
            SET
                duration_seconds =
                    duration_seconds + ?,
                last_seen = ?
            WHERE activity_id = ?
              AND activity_date = ?
        """, (
            event["duration_seconds"],
            event["ended_at"],
            activity_id,
            activity_date
        ))

    connection.commit()

    # 4. Get updated lifetime aggregate
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