from datetime import datetime

from memory.database.db import get_connection


def create_memory(content, context=None, importance_score=None):
    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().isoformat()

    cursor.execute(
        """
        INSERT INTO memories (
            content,
            context,
            importance_score,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            content,
            context,
            importance_score,
            "active",
            created_at
        )
    )

    memory_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return get_memory(memory_id)


def get_memory(memory_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            content,
            context,
            importance_score,
            status,
            created_at
        FROM memories
        WHERE id = ?
        """,
        (memory_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "id": row[0],
        "content": row[1],
        "context": row[2],
        "importance_score": row[3],
        "status": row[4],
        "created_at": row[5]
    }


def get_memories():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            content,
            context,
            importance_score,
            status,
            created_at
        FROM memories
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    memories = []

    for row in rows:
        memories.append({
            "id": row[0],
            "content": row[1],
            "context": row[2],
            "importance_score": row[3],
            "status": row[4],
            "created_at": row[5]
        })

    return memories


def update_memory(
    memory_id,
    content=None,
    context=None,
    importance_score=None,
    status=None
):
    existing_memory = get_memory(memory_id)

    if existing_memory is None:
        return None

    new_content = (
        content
        if content is not None
        else existing_memory["content"]
    )

    new_context = (
        context
        if context is not None
        else existing_memory["context"]
    )

    new_importance_score = (
        importance_score
        if importance_score is not None
        else existing_memory["importance_score"]
    )

    new_status = (
        status
        if status is not None
        else existing_memory["status"]
    )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE memories
        SET
            content = ?,
            context = ?,
            importance_score = ?,
            status = ?
        WHERE id = ?
        """,
        (
            new_content,
            new_context,
            new_importance_score,
            new_status,
            memory_id
        )
    )

    connection.commit()
    connection.close()

    return get_memory(memory_id)


def delete_memory(memory_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM memories
        WHERE id = ?
        """,
        (memory_id,)
    )

    deleted = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return deleted