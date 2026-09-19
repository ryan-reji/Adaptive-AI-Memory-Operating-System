import sqlite3

import pytest

from backend.app.services import evidence_service


@pytest.fixture
def test_database(monkeypatch):
    database_uri = (
        "file:test_activity_evidence"
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

    connection.execute(
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
        evidence_service,
        "get_connection",
        get_test_connection,
    )

    yield connection

    connection.close()


def add_evidence(
    connection,
    *,
    evidence_id,
    source_type,
    timestamp,
    action,
    duration_seconds,
    details,
    created_at,
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
            action,
            duration_seconds,
            details,
            created_at,
        ),
    )

    connection.commit()


def test_get_evidence_returns_evidence_in_descending_order(
    test_database,
):
    add_evidence(
        test_database,
        evidence_id=1,
        source_type="file",
        timestamp="2026-09-18T10:00:00",
        action="modified",
        duration_seconds=5.0,
        details='{"file_name": "one.py"}',
        created_at="2026-09-18T10:00:05",
    )

    add_evidence(
        test_database,
        evidence_id=2,
        source_type="browser",
        timestamp="2026-09-18T11:00:00",
        action="viewed",
        duration_seconds=20.0,
        details='{"title": "FastAPI"}',
        created_at="2026-09-18T11:00:20",
    )

    evidence = evidence_service.get_evidence()

    assert len(evidence) == 2
    assert evidence[0]["id"] == 2
    assert evidence[1]["id"] == 1


def test_get_evidence_supports_pagination(test_database):
    add_evidence(
        test_database,
        evidence_id=1,
        source_type="file",
        timestamp="2026-09-18T10:00:00",
        action="modified",
        duration_seconds=5.0,
        details='{"file_name": "one.py"}',
        created_at="2026-09-18T10:00:05",
    )

    add_evidence(
        test_database,
        evidence_id=2,
        source_type="browser",
        timestamp="2026-09-18T11:00:00",
        action="viewed",
        duration_seconds=20.0,
        details='{"title": "FastAPI"}',
        created_at="2026-09-18T11:00:20",
    )

    add_evidence(
        test_database,
        evidence_id=3,
        source_type="vscode",
        timestamp="2026-09-18T12:00:00",
        action="opened",
        duration_seconds=30.0,
        details='{"project": "Memory OS"}',
        created_at="2026-09-18T12:00:30",
    )

    evidence = evidence_service.get_evidence(
        limit=1,
        offset=1,
    )

    assert len(evidence) == 1
    assert evidence[0]["id"] == 2


def test_get_evidence_by_id_returns_evidence(test_database):
    add_evidence(
        test_database,
        evidence_id=1,
        source_type="browser",
        timestamp="2026-09-18T11:00:00",
        action="viewed",
        duration_seconds=15.0,
        details='{"title": "GitHub"}',
        created_at="2026-09-18T11:00:15",
    )

    evidence = evidence_service.get_evidence_by_id(1)

    assert evidence is not None
    assert evidence["id"] == 1
    assert evidence["source_type"] == "browser"
    assert evidence["action"] == "viewed"
    assert evidence["duration_seconds"] == 15.0
    assert evidence["details"]["title"] == "GitHub"


def test_get_evidence_by_id_returns_none_for_missing_evidence(
    test_database,
):
    assert evidence_service.get_evidence_by_id(999) is None


def test_evidence_does_not_expose_sensitive_details(
    test_database,
):
    add_evidence(
        test_database,
        evidence_id=1,
        source_type="file",
        timestamp="2026-09-18T10:00:00",
        action="modified",
        duration_seconds=5.0,
        details=(
            '{'
            '"path": "C:/Users/Miguel/project/test.py", '
            '"source_path": "C:/Users/Miguel/project/test.py", '
            '"content": "secret content", '
            '"raw": "secret raw data", '
            '"file_name": "test.py", '
            '"action_label": "modified"'
            '}'
        ),
        created_at="2026-09-18T10:00:05",
    )

    evidence = evidence_service.get_evidence_by_id(1)

    assert evidence is not None

    details = evidence["details"]

    assert "path" not in details
    assert "source_path" not in details
    assert "content" not in details
    assert "raw" not in details

    assert details["file_name"] == "test.py"
    assert details["action_label"] == "modified"


def test_evidence_handles_malformed_json_without_leaking_raw_data(
    test_database,
):
    add_evidence(
        test_database,
        evidence_id=1,
        source_type="file",
        timestamp="2026-09-18T10:00:00",
        action="modified",
        duration_seconds=5.0,
        details='{"invalid_json": ',
        created_at="2026-09-18T10:00:05",
    )

    evidence = evidence_service.get_evidence_by_id(1)

    assert evidence is not None
    assert evidence["details"] == {}


def test_evidence_sanitizes_nested_sensitive_details(
    test_database,
):
    add_evidence(
        test_database,
        evidence_id=1,
        source_type="file",
        timestamp="2026-09-18T10:00:00",
        action="modified",
        duration_seconds=5.0,
        details=(
            '{'
            '"metadata": {'
            '"path": "secret/path.py", '
            '"label": "safe"'
            '}, '
            '"items": ['
            '{"source_path": "secret/one.py", "name": "one"}, '
            '{"name": "two"}'
            ']'
            '}'
        ),
        created_at="2026-09-18T10:00:05",
    )

    evidence = evidence_service.get_evidence_by_id(1)

    assert evidence is not None

    details = evidence["details"]

    assert details["metadata"]["label"] == "safe"
    assert "path" not in details["metadata"]

    assert "source_path" not in details["items"][0]
    assert details["items"][0]["name"] == "one"
    assert details["items"][1]["name"] == "two"