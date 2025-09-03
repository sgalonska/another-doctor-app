from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.case import CaseCreate, Case, CaseUpdate
from app.services.case_parser import CaseParserService

router = APIRouter()

@router.post("/", response_model=Case)
def create_case(
    *,
    db: Session = Depends(get_db),
    case_in: CaseCreate,
) -> Any:
    """
    Create new case from uploaded medical records.
    """
    # Parse the case using NLP services
    parser = CaseParserService()
    case_json = parser.parse_medical_text(case_in.raw_text)
    
    # Store in database
    # case = crud.case.create(db=db, obj_in=case_in)
    
    return {"message": "Case parsing not implemented yet", "case_json": case_json}

@router.get("/{case_id}", response_model=Case)
def read_case(
    *,
    db: Session = Depends(get_db),
    case_id: str,
) -> Any:
    """
    Get case by ID.
    """
    # case = crud.case.get(db=db, id=case_id)
    # if not case:
    #     raise HTTPException(status_code=404, detail="Case not found")
    # return case
    return {"message": "Case retrieval not implemented yet"}

@router.get("/", response_model=List[Case])
def read_cases(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve cases.
    """
    # cases = crud.case.get_multi(db=db, skip=skip, limit=limit)
    # return cases
    return {"message": "Cases list not implemented yet"}