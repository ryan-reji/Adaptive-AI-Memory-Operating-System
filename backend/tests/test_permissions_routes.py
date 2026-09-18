from fastapi.testclient import TestClient

from backend.app.api.routes import permissions
from backend.app.main import app


client = TestClient(app)


def test_get_permission_mode_endpoint(monkeypatch):
    monkeypatch.setattr(
        permissions,
        "get_mode",
        lambda: "allow_all",
    )

    response = client.get("/permissions/mode")

    assert response.status_code == 200
    assert response.json() == {
        "mode": "allow_all"
    }


def test_set_permission_mode_endpoint(monkeypatch):
    def fake_set_mode(mode):
        assert mode == "allow_only"
        return "allow_only"

    monkeypatch.setattr(
        permissions,
        "set_mode",
        fake_set_mode,
    )

    response = client.put(
        "/permissions/mode",
        json={
            "mode": "allow_only"
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "mode": "allow_only"
    }


def test_set_permission_mode_rejects_invalid_mode(monkeypatch):
    def fake_set_mode(mode):
        raise ValueError(
            "Permission mode must be 'allow_all' or 'allow_only'."
        )

    monkeypatch.setattr(
        permissions,
        "set_mode",
        fake_set_mode,
    )

    response = client.put(
        "/permissions/mode",
        json={
            "mode": "invalid"
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": (
            "Permission mode must be "
            "'allow_all' or 'allow_only'."
        )
    }


def test_get_exclusions_endpoint(monkeypatch):
    monkeypatch.setattr(
        permissions,
        "get_exclusions",
        lambda: [
            {"path": "C:/Projects/Secret"}
        ],
    )

    response = client.get(
        "/permissions/exclusions"
    )

    assert response.status_code == 200
    assert response.json() == [
        {"path": "C:/Projects/Secret"}
    ]


def test_add_exclusion_endpoint(monkeypatch):
    def fake_add(path):
        assert path == "C:/Projects/Secret"
        return {"path": path}

    monkeypatch.setattr(
        permissions,
        "add_file_exclusion",
        fake_add,
    )

    response = client.post(
        "/permissions/exclusions",
        json={
            "path": "C:/Projects/Secret"
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "path": "C:/Projects/Secret"
    }


def test_remove_exclusion_endpoint(monkeypatch):
    called = {}

    def fake_remove(path):
        called["path"] = path

    monkeypatch.setattr(
        permissions,
        "remove_file_exclusion",
        fake_remove,
    )

    response = client.delete(
        "/permissions/exclusions"
        "?path=C%3A%2FProjects%2FSecret"
    )

    assert response.status_code == 204
    assert called["path"] == "C:/Projects/Secret"


def test_get_allowed_folders_endpoint(monkeypatch):
    monkeypatch.setattr(
        permissions,
        "get_allowed_folders",
        lambda: [
            {"path": "C:/Projects/Allowed"}
        ],
    )

    response = client.get(
        "/permissions/allowed-folders"
    )

    assert response.status_code == 200
    assert response.json() == [
        {"path": "C:/Projects/Allowed"}
    ]


def test_add_allowed_folder_endpoint(monkeypatch):
    def fake_add(path):
        assert path == "C:/Projects/Allowed"
        return {"path": path}

    monkeypatch.setattr(
        permissions,
        "add_file_allowed_folder",
        fake_add,
    )

    response = client.post(
        "/permissions/allowed-folders",
        json={
            "path": "C:/Projects/Allowed"
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "path": "C:/Projects/Allowed"
    }


def test_remove_allowed_folder_endpoint(monkeypatch):
    called = {}

    def fake_remove(path):
        called["path"] = path

    monkeypatch.setattr(
        permissions,
        "remove_file_allowed_folder",
        fake_remove,
    )

    response = client.delete(
        "/permissions/allowed-folders"
        "?path=C%3A%2FProjects%2FAllowed"
    )

    assert response.status_code == 204
    assert called["path"] == "C:/Projects/Allowed"


def test_get_project_folders_endpoint(monkeypatch):
    monkeypatch.setattr(
        permissions,
        "get_project_folders",
        lambda: [
            {
                "path": "C:/Projects/MemoryOS",
                "project_name": "Memory OS",
            }
        ],
    )

    response = client.get(
        "/permissions/project-folders"
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "path": "C:/Projects/MemoryOS",
            "project_name": "Memory OS",
        }
    ]


def test_add_project_folder_endpoint(monkeypatch):
    def fake_add(path, project_name=None):
        assert path == "C:/Projects/MemoryOS"
        assert project_name == "Memory OS"

        return {
            "path": path,
            "project_name": project_name,
        }

    monkeypatch.setattr(
        permissions,
        "add_file_project_folder",
        fake_add,
    )

    response = client.post(
        "/permissions/project-folders",
        json={
            "path": "C:/Projects/MemoryOS",
            "project_name": "Memory OS",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "path": "C:/Projects/MemoryOS",
        "project_name": "Memory OS",
    }


def test_remove_project_folder_endpoint(monkeypatch):
    called = {}

    def fake_remove(path):
        called["path"] = path

    monkeypatch.setattr(
        permissions,
        "remove_file_project_folder",
        fake_remove,
    )

    response = client.delete(
        "/permissions/project-folders"
        "?path=C%3A%2FProjects%2FMemoryOS"
    )

    assert response.status_code == 204
    assert called["path"] == "C:/Projects/MemoryOS"


def test_permission_endpoints_reject_empty_paths():
    response = client.post(
        "/permissions/exclusions",
        json={
            "path": ""
        },
    )

    assert response.status_code == 422


def test_permission_mode_rejects_empty_mode():
    response = client.put(
        "/permissions/mode",
        json={
            "mode": ""
        },
    )

    assert response.status_code == 422