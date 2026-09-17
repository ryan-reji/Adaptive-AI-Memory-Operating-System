from memory.memory_creation.json_manager import mark_processed
from memory.memory_creation.memory_loader import get_unprocessed_memories

from memory.ai_engine.ingestion.memory_adapter import memory_dict_to_record
from memory.ai_engine.ingestion.memory_processor import process_memory
from memory.ai_engine.embeddings.embedder import Embedder
from memory.ai_engine.vector_store.chroma_store import ChromaStore


class MemoryIngestor:
    def __init__(self):
        self.embedder = Embedder()
        self.store = ChromaStore()

    def ingest_unprocessed_memories(self):
        memories = get_unprocessed_memories()

        if not memories:
            return {
                "processed_memory_ids": [],
                "chunks_added": 0
            }

        processed_memory_ids = []
        all_chunks = []

        for memory in memories:
            record = memory_dict_to_record(memory)

            chunks = process_memory(record)

            if chunks:
                all_chunks.extend(chunks)
                processed_memory_ids.append(record.memory_id)

        if not all_chunks:
            return {
                "processed_memory_ids": [],
                "chunks_added": 0
            }

        texts = [
            chunk["content"]
            for chunk in all_chunks
        ]

        embeddings = self.embedder.encode(texts)

        ids = [
            chunk["chunk_id"]
            for chunk in all_chunks
        ]

        metadatas = [
            {
                "memory_id": chunk["memory_id"],
                "source_type": chunk["source_type"],
                "source_name": chunk["source_name"],
                "timestamp": chunk["timestamp"],
                **chunk["metadata"]
            }
            for chunk in all_chunks
        ]

        self.store.add_documents(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

        # Mark memories as AI-processed only after successful
        # embedding and ChromaDB ingestion.
        mark_processed(processed_memory_ids)

        return {
            "processed_memory_ids": processed_memory_ids,
            "chunks_added": len(all_chunks)
        }