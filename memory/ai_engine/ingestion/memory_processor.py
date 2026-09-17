from memory.ai_engine.ingestion.memory_record import MemoryRecord
from memory.ai_engine.ingestion.chunker import chunk_text


def process_memory(record: MemoryRecord) -> list[dict]:
    chunks = chunk_text(record.content)

    processed_chunks = []

    for index, chunk in enumerate(chunks, start=1):
        processed_chunks.append({
            "chunk_id": f"{record.memory_id}_chunk_{index}",
            "content": chunk,
            "memory_id": record.memory_id,
            "source_type": record.source_type,
            "source_name": record.source_name,
            "timestamp": record.timestamp,
            "metadata": record.metadata
        })

    return processed_chunks