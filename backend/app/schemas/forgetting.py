from pydantic import BaseModel


class ForgettingCandidateResponse(BaseModel):
    id: int
    file_name: str
    file_path: str
    label: str
    reason: str
    confidence: float | None = None
    prediction_source: str
    file_size_bytes: int | None = None
    last_scanned_at: str


class ForgettingStatsResponse(BaseModel):
    total_files_scanned: int
    review_candidates: int
    kept: int
    last_scan: str | None = None


class ForgettingActionResponse(BaseModel):
    id: int
    status: str


class ForgettingDismissAllResponse(BaseModel):
    dismissed: int
