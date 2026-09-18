from fastapi.testclient import TestClient

from backend.app.api.routes import evidence
from backend.app.main import app


client = TestClient(app)


def test_get_evidence_endpoint(monkeypatch):
    def fake_get_evidence(limit=50, offset=0):
        assert limit == 50
        assert offset == 0

        return [
            {
                "id": 1,
                "source_type": "browser",
                "timestamp": "2026-09-18T11:00:00",
                "action": "viewed",
                "duration_seconds": 12.0,
                "details": {
                    "title": "FastAPI"
                },
                "created_at": "2026-09-18T11:00:12",
            }
        ]

    monkeypatch.setattr(
        evidence,
        "get_evidence",
        fake_get_evidence,
    )

    response = client.get("/evidence/")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "source_type": "browser",
            "timestamp": "2026-09-18T11:00:00",
            "action": "viewed",
            "duration_seconds": 12.0,
            "details": {
                "title": "FastAPI"
            },
            "created_at": "2026-09-18T11:00:12",
        }
    ]


def test_get_evidence_endpoint_pagination(monkeypatch):
    def fake_get_evidence(limit=50, offset=0):
        assert limit == 10
        assert offset == 20
        return []

    monkeypatch.setattr(
        evidence,
        "get_evidence",
        fake_get_evidence,
    )

    response = client.get(
        "/evidence/?limit=10&offset=20"
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_evidence_endpoint_by_id(monkeypatch):
    def fake_get_evidence_by_id(evidence_id):
        assert evidence_id == 7

        return {
            "id": 7,
            "source_type": "file",
            "timestamp": "2026-09-18T10:00:00",
            "action": "modified",
            "duration_seconds": 5.0,
            "details": {
                "file_name": "test.py"
            },
            "created_at": "2026-09-18T10:00:05",
        }

    monkeypatch.setattr(
        evidence,
        "get_evidence_by_id",
        fake_get_evidence_by_id,
    )

    response = client.get("/evidence/7")

    assert response.status_code == 200
    assert response.json()["id"] == 7
    assert response.json()["source_type"] == "file"


def test_get_evidence_endpoint_not_found(monkeypatch):
    monkeypatch.setattr(
        evidence,
        "get_evidence_by_id",
        lambda evidence_id: None,
    )

    response = client.get("/evidence/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Evidence not found"
    }


def test_get_evidence_rejects_invalid_limit():
    response = client.get(
        "/evidence/?limit=0"
    )

    assert response.status_code == 422


def test_get_evidence_rejects_large_limit():
    response = client.get(
        "/evidence/?limit=201"
    )

    assert response.status_code == 422


def test_get_evidence_rejects_negative_offset():
    response = client.get(
        "/evidence/?offset=-1"
    )

    assert response.status_code == 422