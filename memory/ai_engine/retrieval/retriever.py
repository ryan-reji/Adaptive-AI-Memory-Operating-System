import time

from memory.ai_engine.embeddings.embedder import Embedder
from memory.ai_engine.vector_store.chroma_store import ChromaStore
from memory.ai_engine.retrieval.reranker import HybridReranker


class Retriever:
    def __init__(self, semantic_weight=0.7, keyword_weight=0.3):
        self.embedder = Embedder()
        self.store = ChromaStore()
        self.reranker = HybridReranker(
            semantic_weight=semantic_weight,
            keyword_weight=keyword_weight
        )

    def search(self, query: str, top_k: int = 5):
        start_time = time.perf_counter()

        query_embedding = self.embedder.encode([query])[0]

        candidates = self.store.search(
            query_embedding=query_embedding,
            top_k=10
        )

        documents = candidates["documents"][0]
        metadatas = candidates["metadatas"][0]
        distances = candidates["distances"][0]

        ranked_results = self.reranker.rerank(
            query=query,
            documents=documents,
            semantic_distances=distances
        )

        final_results = []
        seen = set()

        for ranked in ranked_results:
            index = ranked["index"]
            metadata = metadatas[index]
            content = documents[index]

            # Avoid duplicate memories with identical content.
            # Since results are already ranked, the first occurrence
            # is the highest-scoring one.
            duplicate_key = content.strip()

            if duplicate_key in seen:
                continue

            seen.add(duplicate_key)

            final_results.append({
                "content": content,

                "source": (
                    metadata.get("source")
                    or metadata.get("source_name")
                    or "unknown"
                ),

                "source_type": metadata.get(
                    "source_type",
                    "unknown"
                ),

                "source_name": metadata.get(
                    "source_name",
                    metadata.get("source", "unknown")
                ),

                "page": metadata.get("page"),

                "memory_id": metadata.get(
                    "memory_id"
                ),

                "timestamp": metadata.get(
                    "timestamp"
                ),

                "distance": distances[index],
                "semantic_score": ranked["semantic_score"],
                "keyword_score": ranked["keyword_score"],
                "combined_score": ranked["combined_score"]
            })

            if len(final_results) >= top_k:
                break

        retrieval_time_ms = (
            time.perf_counter() - start_time
        ) * 1000

        return {
            "query": query,
            "results": final_results,
            "retrieval_time_ms": retrieval_time_ms
        }