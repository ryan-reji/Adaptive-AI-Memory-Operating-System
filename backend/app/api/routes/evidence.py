from fastapi import APIRouter, HTTPException, Query

from backend.app.schemas.evidence import EvidenceResponse
from backend.app.services.evidence_service import (
    get_evidence,
    get_evidence_by_id,
)


router = APIRouter(
    prefix="/evidence",
    tags=["Evidence"],
)


@router.get(
    "/",
    response_model=list[EvidenceResponse],
)
def get_evidence_endpoint(
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
    return get_evidence(
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{evidence_id}",
    response_model=EvidenceResponse,
)
def get_evidence_by_id_endpoint(evidence_id: int):
    evidence = get_evidence_by_id(evidence_id)

    if evidence is None:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found",
        )

    return evidence