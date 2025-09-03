from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.matching import MatchRequest, MatchResult
from app.services.matching_service import MatchingService

router = APIRouter()

@router.post("/match", response_model=List[MatchResult])
async def match_specialists(
    *,
    db: Session = Depends(get_db),
    match_request: MatchRequest,
) -> Any:
    """
    Find specialist matches for a given case.
    """
    matching_service = MatchingService(db)
    try:
        matches = await matching_service.find_matches(match_request)
        return matches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/case/{case_id}/matches", response_model=List[MatchResult])
def get_case_matches(
    *,
    db: Session = Depends(get_db),
    case_id: str,
    limit: int = 10,
) -> Any:
    """
    Get existing matches for a case.
    """
    return {"message": "Case matches retrieval not implemented yet"}

@router.post("/approve-match")
async def approve_match(
    *,
    db: Session = Depends(get_db),
    case_id: str,
    doctor_id: str,
) -> Any:
    """
    Approve a specialist match and initiate contact.
    """
    return {"message": "Match approval not implemented yet"}

@router.get("/scoring-explanation/{case_id}/{doctor_id}")
def get_scoring_explanation(
    *,
    db: Session = Depends(get_db),
    case_id: str,
    doctor_id: str,
) -> Any:
    """
    Get detailed explanation of how a doctor was scored for a case.
    """
    return {"message": "Scoring explanation not implemented yet"}