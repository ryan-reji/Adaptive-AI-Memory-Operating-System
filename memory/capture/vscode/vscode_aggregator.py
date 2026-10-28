
from memory.database.db import get_connection


def create_activity_key(event):
    """
    Create a stable activity key using project + absolute file path.
    Fall back to project + filename when the full path is unavailable.
    """
    project = (event.get("project") or "Unknown").strip().lower()

    file_path = (event.get("file_path") or "").strip()
    file_name = (event.get("file") or "").strip()

    # Normalize Windows paths so case/slash differences do not
    # create separate activity records.
    if file_path:
        file_identifier = file_path.replace("/", "\\").lower()
    else:
        file_identifier = file_name.lower()

    return f"{project}:{file_identifier}"


def aggregate_vscode_event(event):
    """
    Add a VS Code event to:
    1. The persistent lifetime activity aggregate.
    2. The daily activity history.

    Stores the filename and absolute file path separately.
    """
    activity_key = create_activity_key(event)

    project = (event.get("project") or "Unknown").strip()
    file_name = event.get("file")
    file_path = event.get("file_path")

    duration = float(event.get("duration_seconds") or 0)
    started_at = event["started_at"]
    ended_at = event["ended_at"]

    connection = get_connection()
    cursor = connection.cursor()

    try:
        # -----------------------------------------------------
        # 1. Find an existing lifetime activity
        # -----------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM vscode_activity
            WHERE activity_key = ?
            """,
            (activity_key,)
        )
        row = cursor.fetchone()

        # Compatibility: if this file was previously tracked by
        # filename only, reuse that existing row when possible.
        if row is None and file_path:
            legacy_key = f"{project.lower()}:{(file_name or '').strip().lower()}"

            cursor.execute(
                """
                SELECT id
                FROM vscode_activity
                WHERE activity_key = ?
                """,
                (legacy_key,)
            )
            row = cursor.fetchone()

            if row is not None:
                cursor.execute(
                    """
                    UPDATE vscode_activity
                    SET activity_key = ?, file_path = ?
                    WHERE id = ?
                    """,
                    (activity_key, file_path, row[0])
                )

        if row is None:
            # ---------------------------------------------
            # First recorded activity for this file
            # ---------------------------------------------

            cursor.execute(
                """
                INSERT INTO vscode_activity (
                    activity_key,
                    project,
                    file,
                    file_path,
                    total_duration_seconds,
                    session_count,
                    first_seen,
                    last_seen
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    activity_key,
                    project,
                    file_name,
                    file_path,
                    duration,
                    1,
                    started_at,
                    ended_at
                )
            )

            activity_id = cursor.lastrowid

        else:
            # ---------------------------------------------
            # Update existing lifetime activity
            # ---------------------------------------------

            activity_id = row[0]

            cursor.execute(
                """
                UPDATE vscode_activity
                SET
                    project = ?,
                    file = COALESCE(?, file),
                    file_path = COALESCE(?, file_path),
                    total_duration_seconds =
                        total_duration_seconds + ?,
                    session_count = session_count + 1,
                    last_seen = ?
                WHERE id = ?
                """,
                (
                    project,
                    file_name,
                    file_path,
                    duration,
                    ended_at,
                    activity_id
                )
            )

        # -----------------------------------------------------
        # 2. Determine the activity date
        # -----------------------------------------------------

        activity_date = started_at[:10]

        # -----------------------------------------------------
        # 3. Find daily activity for this file and date
        # -----------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM vscode_daily_activity
            WHERE activity_id = ?
              AND activity_date = ?
            """,
            (activity_id, activity_date)
        )
        daily_row = cursor.fetchone()

        if daily_row is None:
            # First activity for this file on this date
            cursor.execute(
                """
                INSERT INTO vscode_daily_activity (
                    activity_id,
                    activity_date,
                    first_seen,
                    last_seen,
                    duration_seconds
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    activity_id,
                    activity_date,
                    started_at,
                    ended_at,
                    duration
                )
            )

        else:
            # Add this session to the existing daily total
            cursor.execute(
                """
                UPDATE vscode_daily_activity
                SET
                    duration_seconds = duration_seconds + ?,
                    last_seen = ?
                WHERE activity_id = ?
                  AND activity_date = ?
                """,
                (
                    duration,
                    ended_at,
                    activity_id,
                    activity_date
                )
            )

        # -----------------------------------------------------
        # 4. Retrieve the updated lifetime aggregate
        # -----------------------------------------------------

        cursor.execute(
            """
            SELECT
                project,
                file,
                file_path,
                total_duration_seconds,
                session_count,
                first_seen,
                last_seen
            FROM vscode_activity
            WHERE id = ?
            """,
            (activity_id,)
        )
        result = cursor.fetchone()

        connection.commit()

        return {
            "source_type": "vscode",
            "project": result[0],
            "file": result[1],
            "file_path": result[2],
            "total_duration_seconds": result[3],
            "sessions": result[4],
            "first_seen": result[5],
            "last_seen": result[6]
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
