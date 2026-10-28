from fastapi import APIRouter, HTTPException

from backend.app.schemas.forgetting import (
    ForgettingActionResponse,
    ForgettingCandidateResponse,
    ForgettingDismissAllResponse,
    ForgettingStatsResponse,
)
from backend.app.services.forgetting_service import (
    dismiss_all_candidates,
    dismiss_candidate,
    get_forgetting_candidates,
    get_forgetting_stats,
    keep_file,
)


router = APIRouter(
    prefix="/forgetting",
    tags=["Forgetting"],
)


@router.get(
    "/candidates",
    response_model=list[ForgettingCandidateResponse],
)
def get_forgetting_candidates_endpoint():
    return get_forgetting_candidates()


@router.get(
    "/stats",
    response_model=ForgettingStatsResponse,
)
def get_forgetting_stats_endpoint():
    return get_forgetting_stats()


@router.post(
    "/candidates/dismiss-all",
    response_model=ForgettingDismissAllResponse,
)
def dismiss_all_candidates_endpoint():
    return {
        "dismissed": dismiss_all_candidates(),
    }


@router.post(
    "/{candidate_id}/keep",
    response_model=ForgettingActionResponse,
)
def keep_candidate_endpoint(candidate_id: int):
    updated = keep_file(candidate_id)

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    return {
        "id": candidate_id,
        "status": "kept",
    }


@router.post(
    "/{candidate_id}/dismiss",
    response_model=ForgettingActionResponse,
)
def dismiss_candidate_endpoint(candidate_id: int):
    deleted = dismiss_candidate(candidate_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    return {
        "id": candidate_id,
        "status": "dismissed",
    }
