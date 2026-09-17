from memory.ai_engine.ingestion.memory_record import MemoryRecord


record = MemoryRecord(
    memory_id="mem_001",
    source_type="vscode",
    source_name="Adaptive-AI-Memory-Operating-System",
    content="User worked on the RAG pipeline.",
    timestamp="2026-09-17T11:30:00",
    metadata={
        "language": "python"
    }
)

print("Memory Record")
print("-" * 50)
print(record)