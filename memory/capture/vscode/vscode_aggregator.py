from memory.database.db import get_connection


def create_activity_key(event):
    """
    Create a stable key using project + file.
    """

    project = (event.get("project") or "").strip().lower()
    file = (event.get("file") or "").strip().lower()

    return f"{project}:{file}"


def aggregate_vscode_event(event):
    """
    Add a VS Code event to:
    1. The persistent lifetime activity aggregate.
    2. The daily activity history.
    """

    activity_key = create_activity_key(event)

    connection = get_connection()
    cursor = connection.cursor()

    # ---------------------------------------------------------
    # 1. Find existing lifetime activity
    # ---------------------------------------------------------

    cursor.execute("""
        SELECT id
        FROM vscode_activity
        WHERE activity_key = ?
    """, (activity_key,))

    row = cursor.fetchone()

    if row is None:

        cursor.execute("""
            INSERT INTO vscode_activity (
                activity_key,
                project,
                file,
                total_duration_seconds,
                session_count,
                first_seen,
                last_seen
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            activity_key,
            event.get("project"),
            event.get("file"),
            event["duration_seconds"],
            1,
            event["started_at"],
            event["ended_at"]
        ))

        activity_id = cursor.lastrowid

    else:

        activity_id = row[0]

        cursor.execute("""
            UPDATE vscode_activity
            SET
                total_duration_seconds =
                    total_duration_seconds + ?,
                session_count =
                    session_count + 1,
                last_seen = ?
            WHERE activity_key = ?
        """, (
            event["duration_seconds"],
            event["ended_at"],
            activity_key
        ))

    # ---------------------------------------------------------
    # 2. Determine activity date
    # ---------------------------------------------------------

    activity_date = event["started_at"][:10]

    # ---------------------------------------------------------
    # 3. Find daily activity for this activity + date
    # ---------------------------------------------------------

    cursor.execute("""
        SELECT id
        FROM vscode_daily_activity
        WHERE activity_id = ?
          AND activity_date = ?
    """, (
        activity_id,
        activity_date
    ))

    daily_row = cursor.fetchone()

    if daily_row is None:

        # -----------------------------------------------------
        # First activity for this file on this day
        # -----------------------------------------------------

        cursor.execute("""
            INSERT INTO vscode_daily_activity (
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

        # -----------------------------------------------------
        # Activity already exists for this day
        # Update the same daily row
        # -----------------------------------------------------

        cursor.execute("""
            UPDATE vscode_daily_activity
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

    # ---------------------------------------------------------
    # 4. Get updated lifetime aggregate
    # ---------------------------------------------------------

    cursor.execute("""
        SELECT
            project,
            file,
            total_duration_seconds,
            session_count,
            first_seen,
            last_seen
        FROM vscode_activity
        WHERE activity_key = ?
    """, (activity_key,))

    result = cursor.fetchone()

    connection.close()

    return {
        "source_type": "vscode",
        "project": result[0],
        "file": result[1],
        "total_duration_seconds": result[2],
        "sessions": result[3],
        "first_seen": result[4],
        "last_seen": result[5]
    }