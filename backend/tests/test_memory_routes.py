from fastapi.testclient import TestClient

from backend.app.api.routes import memories
from backend.app.main import app


client = TestClient(app)


def test_get_memories_endpoint(monkeypatch):
    def fake_get_memories(limit=50, offset=0):
        assert limit == 50
        assert offset == 0

        return [
            {
                "id": 1,
                "evidence_id": 10,
                "source_type": "file",
                "timestamp": "2026-09-18T10:00:00",
                "action": "modified",
                "duration_seconds": 5.0,
                "details": {
                    "file_name": "test.py"
                },
                "created_at": "2026-09-18T10:00:05",
                "status": "active",
                "ai_processed": False,
            }
        ]

    monkeypatch.setattr(
        memories,
        "get_memories",
        fake_get_memories,
    )

    response = client.get("/memories/")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "evidence_id": 10,
            "source_type": "file",
            "timestamp": "2026-09-18T10:00:00",
            "action": "modified",
            "duration_seconds": 5.0,
            "details": {
                "file_name": "test.py"
            },
            "created_at": "2026-09-18T10:00:05",
            "status": "active",
            "ai_processed": False,
        }
    ]


def test_get_memories_endpoint_pagination(monkeypatch):
    def fake_get_memories(limit=50, offset=0):
        assert limit == 10
        assert offset == 20
        return []

    monkeypatch.setattr(
        memories,
        "get_memories",
        fake_get_memories,
    )

    response = client.get(
        "/memories/?limit=10&offset=20"
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_memory_endpoint(monkeypatch):
    def fake_get_memory(memory_id):
        assert memory_id == 7

        return {
            "id": 7,
            "evidence_id": 17,
            "source_type": "browser",
            "timestamp": "2026-09-18T11:00:00",
            "action": "viewed",
            "duration_seconds": 12.0,
            "details": {
                "title": "FastAPI"
            },
            "created_at": "2026-09-18T11:00:12",
            "status": "active",
            "ai_processed": True,
        }

    monkeypatch.setattr(
        memories,
        "get_memory",
        fake_get_memory,
    )

    response = client.get("/memories/7")

    assert response.status_code == 200
    assert response.json()["id"] == 7
    assert response.json()["ai_processed"] is True


def test_get_memory_endpoint_not_found(monkeypatch):
    monkeypatch.setattr(
        memories,
        "get_memory",
        lambda memory_id: None,
    )

    response = client.get("/memories/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Memory not found"
    }


def test_get_memories_rejects_invalid_limit():
    response = client.get("/memories/?limit=0")

    assert response.status_code == 422


def test_get_memories_rejects_large_limit():
    response = client.get("/memories/?limit=201")

    assert response.status_code == 422