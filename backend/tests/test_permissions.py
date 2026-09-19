import sqlite3

import pytest

from backend.app.services import permissions_service
from memory.capture.common import permissions


@pytest.fixture
def test_database(monkeypatch):
    database_uri = (
        "file:test_permissions"
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
        CREATE TABLE file_permission_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            permission_mode TEXT NOT NULL DEFAULT 'allow_all',
            updated_at TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        INSERT INTO file_permission_settings (
            id,
            permission_mode,
            updated_at
        )
        VALUES (1, 'allow_all', '2026-09-18T10:00:00')
        """
    )

    connection.execute(
        """
        CREATE TABLE file_exclusions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE file_allowed_folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE project_folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL UNIQUE,
            project_name TEXT,
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
        permissions_service,
        "get_connection",
        get_test_connection,
    )

    monkeypatch.setattr(
        permissions,
        "get_connection",
        get_test_connection,
    )

    yield connection

    connection.close()


def test_get_mode_returns_current_mode(test_database):
    assert permissions_service.get_mode() == "allow_all"


def test_set_mode_updates_mode(test_database):
    assert permissions_service.set_mode("allow_only") == "allow_only"
    assert permissions_service.get_mode() == "allow_only"


def test_set_mode_rejects_invalid_mode(test_database):
    with pytest.raises(ValueError):
        permissions_service.set_mode("invalid_mode")


def test_exclusions_crud(test_database, tmp_path):
    folder = tmp_path / "excluded"

    added = permissions_service.add_file_exclusion(
        str(folder)
    )

    assert added["path"] == str(folder)

    exclusions = permissions_service.get_exclusions()

    assert len(exclusions) == 1

    permissions_service.remove_file_exclusion(
        str(folder)
    )

    assert permissions_service.get_exclusions() == []


def test_allowed_folders_crud(test_database, tmp_path):
    folder = tmp_path / "allowed"

    added = permissions_service.add_file_allowed_folder(
        str(folder)
    )

    assert added["path"] == str(folder)

    folders = permissions_service.get_allowed_folders()

    assert len(folders) == 1

    permissions_service.remove_file_allowed_folder(
        str(folder)
    )

    assert permissions_service.get_allowed_folders() == []


def test_project_folders_crud(test_database, tmp_path):
    folder = tmp_path / "project"

    added = permissions_service.add_file_project_folder(
        str(folder),
        project_name="Memory OS",
    )

    assert added["path"] == str(folder)
    assert added["project_name"] == "Memory OS"

    projects = permissions_service.get_project_folders()

    assert len(projects) == 1
    assert projects[0]["path"] == str(folder)
    assert projects[0]["project_name"] == "Memory OS"

    permissions_service.remove_file_project_folder(
        str(folder)
    )

    assert permissions_service.get_project_folders() == []


def test_folder_lists_are_sorted(test_database, tmp_path):
    second = tmp_path / "z-folder"
    first = tmp_path / "a-folder"

    permissions_service.add_file_exclusion(
        str(second)
    )

    permissions_service.add_file_exclusion(
        str(first)
    )

    exclusions = permissions_service.get_exclusions()

    assert exclusions[0]["path"] < exclusions[1]["path"]