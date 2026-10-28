import importlib
import os
import subprocess
import sys
import uuid

import numpy as np


WRITER_SCRIPT = r"""
import sys

import numpy as np

from memory.ai_engine.vector_store.chroma_store import ChromaStore

doc_id = sys.argv[1]
text = sys.argv[2]

store = ChromaStore()

store.add_documents(
    ids=[doc_id],
    documents=[text],
    embeddings=np.array([[1.0, 0.0, 0.0]], dtype=np.float32),
    metadatas=[{"test": True, "doc_id": doc_id}],
)
"""


def test_http_chroma_sees_cross_process_write():
    collection_name = f"test_cross_process_{uuid.uuid4().hex}"
    document_id = f"fresh_{uuid.uuid4().hex}"
    document_text = "FRESH CROSS PROCESS CHROMA DOCUMENT"

    os.environ["CHROMA_COLLECTION"] = collection_name

    store = None

    try:
        import memory.ai_engine.vector_store.chroma_store as chroma_store

        chroma_store = importlib.reload(chroma_store)
        store = chroma_store.ChromaStore()

        store.heartbeat()

        # Warm the existing collection/index before the external writer runs.
        store.add_documents(
            ids=["initial_document"],
            documents=["INITIAL DOCUMENT"],
            embeddings=np.array([[0.0, 1.0, 0.0]], dtype=np.float32),
            metadatas=[{"test": True}],
        )

        store.search(
            query_embedding=np.array(
                [0.0, 1.0, 0.0],
                dtype=np.float32,
            ),
            top_k=1,
        )

        # Write the new document from a separate OS process.
        subprocess.run(
            [
                sys.executable,
                "-c",
                WRITER_SCRIPT,
                document_id,
                document_text,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        # Use the SAME ChromaStore / SAME held collection object.
        results = store.search(
            query_embedding=np.array(
                [1.0, 0.0, 0.0],
                dtype=np.float32,
            ),
            top_k=1,
        )

        assert results["documents"][0][0] == document_text

    finally:
        if store is not None:
            try:
                store.client.delete_collection(name=collection_name)
            except Exception:
                pass

        os.environ.pop("CHROMA_COLLECTION", None)
