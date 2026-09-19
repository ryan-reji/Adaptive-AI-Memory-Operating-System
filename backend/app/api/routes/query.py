from fastapi import APIRouter, HTTPException

from backend.app.schemas.query import (
    QueryRequest,
    QueryResponse,
)
from backend.app.services.rag_service import (
    RAGServiceUnavailable,
    answer_query,
)


router = APIRouter(
    prefix="/query",
    tags=["Query"],
)


@router.post(
    "/",
    response_model=QueryResponse,
)
def query_memory(request: QueryRequest):
    try:
        return answer_query(
            query=request.query,
            top_k=request.top_k,
        )
    except RAGServiceUnavailable as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error