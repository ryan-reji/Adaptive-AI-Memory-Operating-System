from pydantic import BaseModel


class MemoryCreate(BaseModel):
    content: str
    context: str | None = None
    importance_score: float | None = None


class MemoryUpdate(BaseModel):
    content: str | None = None
    context: str | None = None
    importance_score: float | None = None
    status: str | None = None