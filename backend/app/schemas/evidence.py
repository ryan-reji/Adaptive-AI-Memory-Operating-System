from typing import Any

from pydantic import BaseModel


class EvidenceResponse(BaseModel):
    id: int
    source_type: str
    timestamp: str
    action: str | None = None
    duration_seconds: float | None = None
    details: dict[str, Any]
    created_at: str