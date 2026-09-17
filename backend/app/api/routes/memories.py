from fastapi import APIRouter, HTTPException

from backend.app.schemas.memory import MemoryCreate, MemoryUpdate
from backend.app.services.memory_service import (
    create_memory,
    get_memory,
    get_memories,
    update_memory,
    delete_memory
)


router = APIRouter(
    prefix="/memories",
    tags=["Memories"]
)


@router.post("/")
def create_memory_endpoint(memory: MemoryCreate):
    return create_memory(
        content=memory.content,
        context=memory.context,
        importance_score=memory.importance_score
    )


@router.get("/")
def get_memories_endpoint():
    return get_memories()


@router.get("/{memory_id}")
def get_memory_endpoint(memory_id: int):
    memory = get_memory(memory_id)

    if memory is None:
        raise HTTPException(
            status_code=404,
            detail="Memory not found"
        )

    return memory


@router.put("/{memory_id}")
def update_memory_endpoint(
    memory_id: int,
    memory: MemoryUpdate
):
    updated_memory = update_memory(
        memory_id=memory_id,
        content=memory.content,
        context=memory.context,
        importance_score=memory.importance_score,
        status=memory.status
    )

    if updated_memory is None:
        raise HTTPException(
            status_code=404,
            detail="Memory not found"
        )

    return updated_memory


@router.delete("/{memory_id}")
def delete_memory_endpoint(memory_id: int):
    deleted = delete_memory(memory_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Memory not found"
        )

    return {
        "message": "Memory deleted successfully"
    }