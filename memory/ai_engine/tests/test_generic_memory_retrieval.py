from memory.ai_engine.retrieval.retriever import Retriever


retriever = Retriever()

query = "What did I work on with the RAG pipeline and Ollama?"

result = retriever.search(
    query=query,
    top_k=5
)

print("\n" + "=" * 70)
print("QUERY")
print("=" * 70)
print(query)

print("\n" + "=" * 70)
print("RETRIEVED MEMORIES")
print("=" * 70)

for i, item in enumerate(result["results"], start=1):
    print(f"\n--- Result {i} ---")
    print("Source type:", item.get("source_type", "N/A"))
    print("Source:", item["source"])
    print("Page:", item["page"])
    print("Content:", item["content"][:300])
    print("Combined score:", item["combined_score"])