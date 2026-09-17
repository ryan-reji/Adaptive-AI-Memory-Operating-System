from memory.ai_engine.retrieval.retriever import Retriever


retriever = Retriever(
    semantic_weight=0.7,
    keyword_weight=0.3
)

queries = [
    "What are the challenges of Retrieval-Augmented Generation?",
    "How does RAG reduce hallucinations?",
    "How can retrieval precision be improved in RAG?"
]

for query in queries:

    results = retriever.search(query, top_k=5)

    print("\n" + "=" * 70)
    print("QUERY:", query)
    print(f"Retrieval time: {results['retrieval_time_ms']:.2f} ms")
    print("=" * 70)

    for i, result in enumerate(results["results"], start=1):
        print(f"\n--- Result {i} ---")
        print("Page:", result["page"])
        print("Combined score:", f"{result['combined_score']:.4f}")
        print("Semantic score:", f"{result['semantic_score']:.4f}")
        print("Keyword score:", f"{result['keyword_score']:.4f}")
        print("Content:")
        print(result["content"][:300])