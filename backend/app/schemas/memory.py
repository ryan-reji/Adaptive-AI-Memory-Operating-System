from typing import Any

from pydantic import BaseModel


class MemoryResponse(BaseModel):
    id: int
    evidence_id: int
    source_type: str
    timestamp: str
    action: str | None = None
    duration_seconds: float | None = None
    details: dict[str, Any]
    created_at: str
    status: str
    ai_processed: bool