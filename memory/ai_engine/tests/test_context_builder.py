from memory.ai_engine.retrieval.retriever import Retriever
from memory.ai_engine.rag.context_builder import ContextBuilder


retriever = Retriever()

query = "How does RAG reduce hallucinations?"

retrieval = retriever.search(query, top_k=3)

builder = ContextBuilder()

context = builder.build(
    retrieval["results"]
)

print("\n" + "=" * 70)
print("RAG CONTEXT")
print("=" * 70)
print(context)