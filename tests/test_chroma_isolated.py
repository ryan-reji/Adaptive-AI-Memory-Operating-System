import os
import uuid

import chromadb

from memory.ai_engine.embeddings.embedder import Embedder
from memory.ai_engine.ingestion.memory_ingestor import (
    sanitize_chroma_metadata,
)


def main():
    host = os.getenv("CHROMA_HOST", "127.0.0.1")
    port = int(os.getenv("CHROMA_PORT", "8001"))

    client = chromadb.HttpClient(host=host, port=port)

    collection_name = f"ingestion_test_{uuid.uuid4().hex[:10]}"
    collection = None

    try:
        collection = client.create_collection(name=collection_name)

        text = (
            "Synthetic test memory: the user worked on "
            "the Adaptive AI Memory OS retrieval system."
        )

        metadata = sanitize_chroma_metadata({
            "memory_id": "synthetic_test_001",
            "source_type": "test",
            "source_name": "synthetic_test",
            "timestamp": "2026-10-30T12:00:00",
            "optional_value": None,
            "test_details": {"purpose": "isolated ingestion test"},
        })

        embedder = Embedder()
        embedding = embedder.encode([text])

        collection.upsert(
            ids=["synthetic_test_001"],
            documents=[text],
            embeddings=embedding.tolist(),
            metadatas=[metadata],
        )

        print("DOCUMENT COUNT:", collection.count())

        result = collection.query(
            query_embeddings=embedding.tolist(),
            n_results=1,
        )

        print("RETRIEVED DOCUMENT:", result["documents"][0][0])
        print("RETRIEVED METADATA:", result["metadatas"][0][0])

        assert collection.count() == 1
        assert result["ids"][0][0] == "synthetic_test_001"

        print("RESULT: CHROMADB WRITE AND RETRIEVAL SUCCESSFUL")

    finally:
        if collection is not None:
            client.delete_collection(name=collection_name)
            print("TEMPORARY TEST COLLECTION DELETED")


if __name__ == "__main__":
    main()