import sqlite3

import pytest

from backend.app.services import memory_service


@pytest.fixture
def test_database(monkeypatch):
    database_uri = (
        "file:test_memory_records"
        "?mode=memory"
        "&cache=shared"
    )

    connection = sqlite3.connect(
        database_uri,
        uri=True,
    )

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE activity_evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            action TEXT,
            duration_seconds REAL,
            details TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE memory_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evidence_id INTEGER NOT NULL UNIQUE,
            source_type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            action TEXT,
            duration_seconds REAL,
            details TEXT,
            created_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            ai_processed INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (evidence_id)
                REFERENCES activity_evidence(id)
        )
        """
    )

    connection.commit()

    def get_test_connection():
        test_connection = sqlite3.connect(
            database_uri,
            uri=True,
        )
        test_connection.execute(
            "PRAGMA foreign_keys = ON"
        )
        return test_connection

    monkeypatch.setattr(
        memory_service,
        "get_connection",
        get_test_connection,
    )

    yield connection

    connection.close()


def add_memory(
    connection,
    *,
    evidence_id,
    source_type,
    timestamp,
    details,
    status="active",
    ai_processed=0,
):
    connection.execute(
        """
        INSERT INTO activity_evidence (
            id,
            source_type,
            timestamp,
            action,
            duration_seconds,
            details,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            evidence_id,
            source_type,
            timestamp,
            "test action",
            10.0,
            details,
            timestamp,
        ),
    )

    connection.execute(
        """
        INSERT INTO memory_records (
            evidence_id,
            source_type,
            timestamp,
            action,
            duration_seconds,
            details,
            created_at,
            status,
            ai_processed
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            evidence_id,
            source_type,
            timestamp,
            "test action",
            10.0,
            details,
            timestamp,
            status,
            ai_processed,
        ),
    )

    connection.commit()


def test_get_memories_returns_active_memories(test_database):
    add_memory(
        test_database,
        evidence_id=1,
        source_type="file",
        timestamp="2026-09-18T10:00:00",
        details='{"path": "project/test.py"}',
        ai_processed=0,
    )

    add_memory(
        test_database,
        evidence_id=2,
        source_type="browser",
        timestamp="2026-09-18T11:00:00",
        details='{"title": "FastAPI"}',
        ai_processed=1,
    )

    add_memory(
        test_database,
        evidence_id=3,
        source_type="vscode",
        timestamp="2026-09-18T12:00:00",
        details='{"project": "Memory OS"}',
        status="inactive",
    )

    memories = memory_service.get_memories()

    assert len(memories) == 2
    assert memories[0]["id"] > memories[1]["id"]
    assert memories[0]["source_type"] == "browser"
    assert memories[0]["ai_processed"] is True
    assert memories[1]["ai_processed"] is False


def test_get_memories_supports_pagination(test_database):
    add_memory(
        test_database,
        evidence_id=1,
        source_type="file",
        timestamp="2026-09-18T10:00:00",
        details='{"path": "one"}',
    )

    add_memory(
        test_database,
        evidence_id=2,
        source_type="browser",
        timestamp="2026-09-18T11:00:00",
        details='{"title": "two"}',
    )

    add_memory(
        test_database,
        evidence_id=3,
        source_type="vscode",
        timestamp="2026-09-18T12:00:00",
        details='{"project": "three"}',
    )

    memories = memory_service.get_memories(
        limit=1,
        offset=1,
    )

    assert len(memories) == 1
    assert memories[0]["source_type"] == "browser"


def test_get_memory_returns_active_memory(test_database):
    add_memory(
        test_database,
        evidence_id=1,
        source_type="file",
        timestamp="2026-09-18T10:00:00",
        details='{"path": "project/test.py", "action": "modified"}',
    )

    memory = memory_service.get_memory(1)

    assert memory is not None
    assert memory["id"] == 1
    assert memory["evidence_id"] == 1

    # Safe metadata should remain available.
    assert memory["details"]["action"] == "modified"

    # Sensitive filesystem information must not be exposed.
    assert "path" not in memory["details"]


def test_get_memory_returns_none_for_missing_memory(test_database):
    assert memory_service.get_memory(999) is None


def test_get_memory_does_not_return_inactive_memory(test_database):
    add_memory(
        test_database,
        evidence_id=1,
        source_type="file",
        timestamp="2026-09-18T10:00:00",
        details='{"path": "project/test.py"}',
        status="inactive",
    )

    assert memory_service.get_memory(1) is None


def test_memory_response_does_not_expose_sensitive_details(test_database):
    add_memory(
        test_database,
        evidence_id=1,
        source_type="file",
        timestamp="2026-09-18T10:00:00",
        details=(
            '{'
            '"source_path": "C:/Users/Miguel/project/test.py", '
            '"old_path": "C:/Users/Miguel/project/old.py", '
            '"content": "secret file content", '
            '"path": "C:/Users/Miguel/project/test.py", '
            '"raw": "raw sensitive data", '
            '"file_name": "test.py", '
            '"file_type": "python", '
            '"file_size": 1234, '
            '"action": "modified", '
            '"description": "Test file changed"'
            '}'
        ),
    )

    memory = memory_service.get_memory(1)

    assert memory is not None

    details = memory["details"]

    # Sensitive values must not be exposed.
    assert "source_path" not in details
    assert "old_path" not in details
    assert "path" not in details
    assert "content" not in details
    assert "raw" not in details

    # Safe metadata should still be returned.
    assert details["file_name"] == "test.py"
    assert details["file_type"] == "python"
    assert details["file_size"] == 1234
    assert details["action"] == "modified"
    assert details["description"] == "Test file changed"


def test_memory_response_does_not_expose_malformed_raw_details(test_database):
    add_memory(
        test_database,
        evidence_id=1,
        source_type="file",
        timestamp="2026-09-18T10:00:00",
        details='{"invalid_json": ',
    )

    memory = memory_service.get_memory(1)

    assert memory is not None
    assert memory["details"] == {}
    assert "raw" not in memory["details"]