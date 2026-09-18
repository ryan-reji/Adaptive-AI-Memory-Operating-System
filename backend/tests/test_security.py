from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_unknown_route_returns_404():
    response = client.get("/this-route-does-not-exist")

    assert response.status_code == 404


def test_memory_endpoint_rejects_invalid_limit():
    response = client.get("/memories/?limit=0")

    assert response.status_code == 422


def test_memory_endpoint_rejects_excessive_limit():
    response = client.get("/memories/?limit=201")

    assert response.status_code == 422


def test_evidence_endpoint_rejects_invalid_limit():
    response = client.get("/evidence/?limit=0")

    assert response.status_code == 422


def test_evidence_endpoint_rejects_excessive_limit():
    response = client.get("/evidence/?limit=201")

    assert response.status_code == 422


def test_evidence_endpoint_rejects_negative_offset():
    response = client.get("/evidence/?offset=-1")

    assert response.status_code == 422


def test_permission_endpoint_rejects_empty_path():
    response = client.post(
        "/permissions/exclusions",
        json={"path": ""},
    )

    assert response.status_code == 422


def test_permission_endpoint_rejects_excessive_path():
    response = client.post(
        "/permissions/exclusions",
        json={"path": "x" * 4097},
    )

    assert response.status_code == 422


def test_query_endpoint_rejects_empty_query():
    response = client.post(
        "/query/",
        json={"query": ""},
    )

    assert response.status_code == 422


def test_query_endpoint_rejects_excessive_query():
    response = client.post(
        "/query/",
        json={"query": "x" * 2001},
    )

    assert response.status_code == 422


def test_unexpected_exception_does_not_expose_internal_details(
    monkeypatch,
):
    from backend.app.api.routes import memories

    def failing_get_memories(limit=50, offset=0):
        raise RuntimeError(
            "SECRET DATABASE PATH / internal stack trace"
        )

    monkeypatch.setattr(
        memories,
        "get_memories",
        failing_get_memories,
    )

    client = TestClient(
        app,
        raise_server_exceptions=False,
    )

    response = client.get("/memories/")

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Internal server error."
    }