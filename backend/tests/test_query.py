from fastapi.testclient import TestClient

from backend.app.api.routes import query
from backend.app.main import app
from backend.app.services.rag_service import RAGServiceUnavailable

client = TestClient(app)


def test_query_endpoint(monkeypatch):
    def fake_answer_query(query, top_k=3):
        assert query == "What was I working on?"
        assert top_k == 3

        return {
            "query": query,
            "answer": "You were working on the memory system.",
            "retrieval_time_ms": 12.5,
        }

    monkeypatch.setattr(
        query,
        "answer_query",
        fake_answer_query,
    )

    response = client.post(
        "/query/",
        json={
            "query": "What was I working on?",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "query": "What was I working on?",
        "answer": "You were working on the memory system.",
        "retrieval_time_ms": 12.5,
    }


def test_query_endpoint_accepts_top_k(monkeypatch):
    def fake_answer_query(query, top_k=3):
        assert query == "test"
        assert top_k == 7

        return {
            "query": query,
            "answer": "test answer",
            "retrieval_time_ms": 5.0,
        }

    monkeypatch.setattr(
        query,
        "answer_query",
        fake_answer_query,
    )

    response = client.post(
        "/query/",
        json={
            "query": "test",
            "top_k": 7,
        },
    )

    assert response.status_code == 200


def test_query_endpoint_rejects_empty_query():
    response = client.post(
        "/query/",
        json={
            "query": "",
        },
    )

    assert response.status_code == 422


def test_query_endpoint_rejects_invalid_top_k():
    response = client.post(
        "/query/",
        json={
            "query": "test",
            "top_k": 0,
        },
    )

    assert response.status_code == 422


def test_query_endpoint_returns_503_when_ai_unavailable(
    monkeypatch,
):
    def unavailable(query, top_k=3):
      raise RAGServiceUnavailable(
        "The AI query service is currently unavailable."
    )

    monkeypatch.setattr(
        query,
        "answer_query",
        unavailable,
    )

    response = client.post(
        "/query/",
        json={
            "query": "test",
        },
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "The AI query service is currently unavailable."
    }