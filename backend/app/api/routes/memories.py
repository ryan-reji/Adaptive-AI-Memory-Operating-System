from fastapi import APIRouter, HTTPException, Query

from backend.app.schemas.memory import MemoryResponse
from backend.app.services.memory_service import (
    get_memory,
    get_memories,
)


router = APIRouter(
    prefix="/memories",
    tags=["Memories"],
)


@router.get(
    "/",
    response_model=list[MemoryResponse],
)
def get_memories_endpoint(
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
):
    return get_memories(
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{memory_id}",
    response_model=MemoryResponse,
)
def get_memory_endpoint(memory_id: int):
    memory = get_memory(memory_id)

    if memory is None:
        raise HTTPException(
            status_code=404,
            detail="Memory not found",
        )

    return memory