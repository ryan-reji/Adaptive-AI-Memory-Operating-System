
import json

from memory.memory_creation.json_manager import mark_processed
from memory.memory_creation.memory_loader import get_unprocessed_memories

from memory.ai_engine.ingestion.memory_adapter import memory_dict_to_record
from memory.ai_engine.ingestion.memory_processor import process_memory
from memory.ai_engine.embeddings.embedder import Embedder
from memory.ai_engine.vector_store.chroma_store import ChromaStore


def sanitize_chroma_metadata(metadata: dict) -> dict:
    """
    ChromaDB metadata supports scalar values.
    Remove None values and serialize nested dictionaries/lists.
    Preserve useful metadata wherever possible.
    """
    clean_metadata = {}

    for key, value in metadata.items():
        if value is None:
            continue

        if isinstance(value, (str, int, float, bool)):
            clean_metadata[key] = value

        elif isinstance(value, (dict, list)):
            clean_metadata[key] = json.dumps(
                value,
                ensure_ascii=False,
                default=str
            )

        else:
            clean_metadata[key] = str(value)

    return clean_metadata


class MemoryIngestor:

    def __init__(self):
        self.embedder = Embedder()
        self.store = ChromaStore()

    def ingest_unprocessed_memories(self):

        memories = get_unprocessed_memories()

        if not memories:
            return {
                "processed_memory_ids": [],
                "chunks_added": 0,
                "failed_memory_ids": [],
                "message": "No unprocessed memories found."
            }

        processed_memory_ids = []
        failed_memory_ids = []
        all_chunks = []

        # Convert memories into chunks independently.
        # A single malformed record should not stop the entire batch.
        for memory in memories:

            try:
                record = memory_dict_to_record(memory)
                chunks = process_memory(record)

                if not chunks:
                    failed_memory_ids.append({
                        "memory_id": record.memory_id,
                        "reason": "No valid text chunks generated."
                    })
                    continue

                all_chunks.extend(chunks)
                processed_memory_ids.append(record.memory_id)

            except Exception as error:
                failed_memory_ids.append({
                    "memory_id": memory.get("memory_id"),
                    "reason": str(error)
                })

        if not all_chunks:
            return {
                "processed_memory_ids": [],
                "chunks_added": 0,
                "failed_memory_ids": failed_memory_ids,
                "message": "No valid chunks available for ingestion."
            }

        try:
            # Generate embeddings.
            texts = [
                chunk["content"]
                for chunk in all_chunks
            ]

            embeddings = self.embedder.encode(texts)

            if len(embeddings) != len(all_chunks):
                raise ValueError(
                    "Embedding count does not match chunk count."
                )

            # Prepare ChromaDB IDs.
            ids = [
                chunk["chunk_id"]
                for chunk in all_chunks
            ]

            # Prepare and sanitize ChromaDB metadata.
            metadatas = []

            for chunk in all_chunks:

                metadata = {
                    "memory_id": chunk["memory_id"],
                    "source_type": chunk["source_type"],
                    "source_name": chunk["source_name"],
                    "timestamp": chunk["timestamp"],
                    **(chunk.get("metadata") or {})
                }

                metadatas.append(
                    sanitize_chroma_metadata(metadata)
                )

            # Write all chunks to ChromaDB.
            self.store.add_documents(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )

            # Mark only successfully ingested memories as processed.
            mark_processed(processed_memory_ids)

            return {
                "processed_memory_ids": processed_memory_ids,
                "chunks_added": len(all_chunks),
                "failed_memory_ids": failed_memory_ids,
                "message": "Memory ingestion completed."
            }

        except Exception:
            # Do not mark records as processed if ingestion fails.
            raise
