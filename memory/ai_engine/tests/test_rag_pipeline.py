from memory.ai_engine.rag.rag_pipeline import RAGPipeline


rag = RAGPipeline()

query = "How does RAG reduce hallucinations?"

result = rag.answer(
    query=query,
    top_k=3
)

print("\n" + "=" * 70)
print("USER QUERY")
print("=" * 70)
print(query)

print("\n" + "=" * 70)
print("GENERATED ANSWER")
print("=" * 70)
print(result["answer"])

print("\n" + "=" * 70)
print("RETRIEVAL TIME")
print("=" * 70)
print(f"{result['retrieval_time_ms']:.2f} ms")