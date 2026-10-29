import sqlite3

from memory.smart_forgetting.config import RECOMMENDATIONS_DB_PATH


def _connect():
    connection = sqlite3.connect(str(RECOMMENDATIONS_DB_PATH))
    connection.row_factory = sqlite3.Row
    return connection


def _zero_stats():
    return {
        "total_files_scanned": 0,
        "review_candidates": 0,
        "kept": 0,
        "last_scan": None,
    }


def get_forgetting_candidates():
    if not RECOMMENDATIONS_DB_PATH.is_file():
        return []

    connection = _connect()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT *
            FROM recommendations
            WHERE label = 'review'
            ORDER BY confidence ASC NULLS LAST
            """,
        )
    except sqlite3.OperationalError:
        connection.close()
        return []

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


def get_forgetting_stats():
    if not RECOMMENDATIONS_DB_PATH.is_file():
        return _zero_stats()

    connection = _connect()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT
                COUNT(*),
                SUM(CASE WHEN label = 'review' THEN 1 ELSE 0 END),
                SUM(CASE WHEN label = 'keep' THEN 1 ELSE 0 END),
                MAX(last_scanned_at)
            FROM recommendations
            """,
        )
    except sqlite3.OperationalError:
        connection.close()
        return _zero_stats()

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return _zero_stats()

    return {
        "total_files_scanned": row[0] or 0,
        "review_candidates": row[1] or 0,
        "kept": row[2] or 0,
        "last_scan": row[3],
    }


def keep_file(candidate_id):
    if not RECOMMENDATIONS_DB_PATH.is_file():
        return None

    connection = _connect()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            UPDATE recommendations
            SET label = 'keep'
            WHERE id = ?
            """,
            (candidate_id,),
        )
    except sqlite3.OperationalError:
        connection.close()
        return None

    rowcount = cursor.rowcount
    connection.commit()
    connection.close()

    return rowcount


def dismiss_candidate(candidate_id):
    if not RECOMMENDATIONS_DB_PATH.is_file():
        return None

    connection = _connect()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            DELETE FROM recommendations
            WHERE id = ?
            """,
            (candidate_id,),
        )
    except sqlite3.OperationalError:
        connection.close()
        return None

    rowcount = cursor.rowcount
    connection.commit()
    connection.close()

    return rowcount


def dismiss_all_candidates():
    if not RECOMMENDATIONS_DB_PATH.is_file():
        return 0

    connection = _connect()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            DELETE FROM recommendations
            WHERE label = 'review'
            """,
        )
    except sqlite3.OperationalError:
        connection.close()
        return 0

    rowcount = cursor.rowcount
    connection.commit()
    connection.close()

    return rowcount
