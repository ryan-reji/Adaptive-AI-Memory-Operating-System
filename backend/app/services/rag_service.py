from functools import lru_cache


class RAGServiceUnavailable(Exception):
    """Raised when the RAG system cannot be used."""


@lru_cache(maxsize=1)
def _get_pipeline():
    try:
        from memory.ai_engine.rag.rag_pipeline import RAGPipeline
    except ImportError as error:
        raise RAGServiceUnavailable(
            "AI dependencies are not installed."
        ) from error

    try:
        return RAGPipeline()
    except Exception as error:
        raise RAGServiceUnavailable(
            "The AI query service could not be initialized."
        ) from error


def answer_query(query: str, top_k: int = 3) -> dict:
    pipeline = _get_pipeline()

    try:
        result = pipeline.answer(
            query=query,
            top_k=top_k,
        )
    except Exception as error:
        raise RAGServiceUnavailable(
            "The AI query service is currently unavailable."
        ) from error

    return {
        "query": result["query"],
        "answer": result["answer"],
        "retrieval_time_ms": result["retrieval_time_ms"],
    }