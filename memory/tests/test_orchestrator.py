from memory import orchestrator


def test_ai_ingestion_is_called_after_memory_processing(monkeypatch):
    calls = []

    class FakeIngestor:
        def ingest_unprocessed_memories(self):
            calls.append("ingest")
            return {
                "processed_memory_ids": [10, 11],
                "chunks_added": 4,
            }

    monkeypatch.setattr(
        orchestrator,
        "_get_memory_ingestor",
        lambda: FakeIngestor(),
    )
    monkeypatch.setattr(
        orchestrator,
        "process_pending_evidence",
        lambda: calls.append("relevance"),
    )
    monkeypatch.setattr(
        orchestrator,
        "process_retained_evidence",
        lambda: calls.append("memory_creation"),
    )
    monkeypatch.setattr(
        orchestrator,
        "update_daily_json",
        lambda: calls.append("json") or [],
    )

    result = orchestrator.run_processing_pipeline()

    assert calls == [
        "relevance",
        "memory_creation",
        "json",
        "ingest",
    ]
    assert result["processed_memory_ids"] == [10, 11]
    assert result["chunks_added"] == 4


def test_ai_ingestion_failure_does_not_stop_pipeline(monkeypatch):
    calls = []

    class FakeIngestor:
        def ingest_unprocessed_memories(self):
            calls.append("ingest")
            raise RuntimeError("ChromaDB unavailable")

    monkeypatch.setattr(
        orchestrator,
        "_get_memory_ingestor",
        lambda: FakeIngestor(),
    )
    monkeypatch.setattr(
        orchestrator,
        "process_pending_evidence",
        lambda: calls.append("relevance"),
    )
    monkeypatch.setattr(
        orchestrator,
        "process_retained_evidence",
        lambda: calls.append("memory_creation"),
    )
    monkeypatch.setattr(
        orchestrator,
        "update_daily_json",
        lambda: calls.append("json") or [],
    )

    result = orchestrator.run_processing_pipeline()

    assert calls == [
        "relevance",
        "memory_creation",
        "json",
        "ingest",
    ]
    assert result["processed_memory_ids"] == []
    assert result["chunks_added"] == 0


def test_memory_ingestor_is_created_only_once(monkeypatch):
    created = []

    class FakeIngestor:
        pass

    def fake_create_ingestor():
        instance = FakeIngestor()
        created.append(instance)
        return instance

    monkeypatch.setattr(
        orchestrator,
        "_ingestor",
        None,
    )
    monkeypatch.setattr(
        orchestrator,
        "_create_memory_ingestor",
        fake_create_ingestor,
    )

    first = orchestrator._get_memory_ingestor()
    second = orchestrator._get_memory_ingestor()

    assert first is second
    assert len(created) == 1
    
def test_earlier_stage_failure_does_not_block_later_stages(
    monkeypatch,
):
    calls = []

    def failing_relevance():
        calls.append("relevance")
        raise RuntimeError("Relevance model unavailable")

    monkeypatch.setattr(
        orchestrator,
        "process_pending_evidence",
        failing_relevance,
    )

    monkeypatch.setattr(
        orchestrator,
        "process_retained_evidence",
        lambda: calls.append("memory_creation"),
    )

    monkeypatch.setattr(
        orchestrator,
        "update_daily_json",
        lambda: calls.append("json") or [],
    )

    class FakeIngestor:
        def ingest_unprocessed_memories(self):
            calls.append("ingest")

            return {
                "processed_memory_ids": [20],
                "chunks_added": 2,
            }

    monkeypatch.setattr(
        orchestrator,
        "_get_memory_ingestor",
        lambda: FakeIngestor(),
    )

    result = orchestrator.run_processing_pipeline()

    assert calls == [
        "relevance",
        "memory_creation",
        "json",
        "ingest",
    ]

    assert result["processed_memory_ids"] == [20]
    assert result["chunks_added"] == 2