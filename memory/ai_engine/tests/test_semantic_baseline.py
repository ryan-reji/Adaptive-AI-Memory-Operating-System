from memory.ai_engine.embeddings.embedder import Embedder
from memory.ai_engine.vector_store.chroma_store import ChromaStore


embedder = Embedder()
store = ChromaStore()

queries = [
    "What are the challenges of Retrieval-Augmented Generation?",
    "How does RAG reduce hallucinations?",
    "How can retrieval precision be improved in RAG?"
]

for query in queries:

    query_embedding = embedder.encode([query])[0]

    results = store.search(
        query_embedding=query_embedding,
        top_k=5
    )

    print("\n" + "=" * 70)
    print("QUERY:", query)
    print("=" * 70)

    for i, (document, metadata, distance) in enumerate(
        zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ),
        start=1
    ):
        print(f"\n--- Result {i} ---")
        print("Page:", metadata["page"])
        print("Distance:", f"{distance:.4f}")
        print("Content:")
        print(document[:300])