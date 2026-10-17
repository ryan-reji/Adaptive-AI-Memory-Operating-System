
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class RAGServiceUnavailable(Exception):
    """Raised when the RAG system cannot be used."""


@lru_cache(maxsize=1)
def _get_pipeline():
    try:
        from memory.ai_engine.rag.rag_pipeline import RAGPipeline
    except ImportError as error:
        logger.exception("Failed to import RAGPipeline")
        raise RAGServiceUnavailable(
            "AI dependencies are not installed."
        ) from error

    try:
        return RAGPipeline()
    except Exception as error:
        logger.exception("Failed to initialize RAGPipeline")
        raise RAGServiceUnavailable(
            f"The AI query service could not be initialized: "
            f"{type(error).__name__}: {error}"
        ) from error


def answer_query(query: str, top_k: int = 3) -> dict:
    pipeline = _get_pipeline()

    try:
        result = pipeline.answer(
            query=query,
            top_k=top_k,
        )
    except Exception as error:
        logger.exception("RAG pipeline query failed")
        raise RAGServiceUnavailable(
            f"The AI query service is currently unavailable: "
            f"{type(error).__name__}: {error}"
        ) from error

    return {
        "query": result["query"],
        "answer": result["answer"],
        "retrieval_time_ms": result["retrieval_time_ms"],
    }
