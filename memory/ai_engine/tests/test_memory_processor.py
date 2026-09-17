from memory.ai_engine.ingestion.memory_record import MemoryRecord
from memory.ai_engine.ingestion.memory_processor import process_memory


record = MemoryRecord(
    memory_id="mem_001",
    source_type="vscode",
    source_name="Adaptive-AI-Memory-Operating-System",
    content=(
        "The user worked on the RAG pipeline. "
        "They created a local LLM client using Ollama. "
        "They tested Qwen3.5 for local response generation."
    ),
    timestamp="2026-09-17T11:30:00",
    metadata={
        "language": "python"
    }
)

chunks = process_memory(record)

print("Chunks created:", len(chunks))

for chunk in chunks:
    print("\n" + "-" * 50)
    print("Chunk ID:", chunk["chunk_id"])
    print("Source:", chunk["source_type"])
    print("Name:", chunk["source_name"])
    print("Timestamp:", chunk["timestamp"])
    print("Content:", chunk["content"])