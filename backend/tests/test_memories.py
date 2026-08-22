import sqlite3

import pytest

from backend.app.services import memory_service


@pytest.fixture
def test_database(monkeypatch):
    connection = sqlite3.connect(
        "file:test_memory?mode=memory&cache=shared",
        uri=True
    )

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            context TEXT,
            importance_score REAL,
            status TEXT DEFAULT 'active',
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()

    def get_test_connection():
        return sqlite3.connect(
            "file:test_memory?mode=memory&cache=shared",
            uri=True
        )

    monkeypatch.setattr(
        memory_service,
        "get_connection",
        get_test_connection
    )

    yield connection

    connection.close()


def test_create_memory(test_database):
    memory = memory_service.create_memory(
        content="Test memory",
        context="testing",
        importance_score=0.8
    )

    assert memory is not None
    assert memory["content"] == "Test memory"
    assert memory["context"] == "testing"
    assert memory["importance_score"] == 0.8
    assert memory["status"] == "active"


def test_get_memory(test_database):
    memory = memory_service.create_memory(
        content="Get test",
        context="testing",
        importance_score=0.5
    )

    result = memory_service.get_memory(memory["id"])

    assert result is not None
    assert result["id"] == memory["id"]


def test_get_memories(test_database):
    memory_service.create_memory(
        content="List test",
        context="testing",
        importance_score=0.6
    )

    memories = memory_service.get_memories()

    assert len(memories) == 1
    assert memories[0]["content"] == "List test"


def test_update_memory(test_database):
    memory = memory_service.create_memory(
        content="Before update",
        context="testing",
        importance_score=0.5
    )

    updated = memory_service.update_memory(
        memory["id"],
        content="After update",
        importance_score=0.9
    )

    assert updated is not None
    assert updated["content"] == "After update"
    assert updated["importance_score"] == 0.9


def test_delete_memory(test_database):
    memory = memory_service.create_memory(
        content="Delete test",
        context="testing",
        importance_score=0.4
    )

    result = memory_service.delete_memory(memory["id"])

    assert result is True
    assert memory_service.get_memory(memory["id"]) is None


def test_get_missing_memory(test_database):
    result = memory_service.get_memory(999)

    assert result is None


def test_update_missing_memory(test_database):
    result = memory_service.update_memory(
        999,
        content="Does not exist"
    )

    assert result is None


def test_delete_missing_memory(test_database):
    result = memory_service.delete_memory(999)

    assert result is False