from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import uuid

class CaseCondition(BaseModel):
    text: str
    icd10: Optional[str] = None
    snomed: Optional[str] = None
    mesh: Optional[str] = None

class CaseAnatomy(BaseModel):
    site: str
    laterality: Optional[str] = None
    arterial_segments: Optional[List[str]] = None

class CasePriorIntervention(BaseModel):
    name: str
    target: Optional[str] = None
    status: Optional[str] = None
    date_approx: Optional[str] = None

class CaseJSON(BaseModel):
    """CaseJSON schema v1 - machine-readable case representation."""
    condition: CaseCondition
    anatomy: CaseAnatomy
    prior_interventions: Optional[List[CasePriorIntervention]] = None
    comorbidities: Optional[List[str]] = None
    goals: Optional[List[str]] = None
    urgency: Optional[str] = "medium"
    keywords: Optional[List[str]] = None
    date_anchor: Optional[str] = None

class CaseCreate(BaseModel):
    raw_text: str
    title: Optional[str] = "Patient Case"
    patient_id: Optional[str] = None

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    casejson: Optional[Dict[str, Any]] = None
    human_brief: Optional[str] = None
    synthetic_abstract: Optional[str] = None

class Case(BaseModel):
    case_id: uuid.UUID
    casejson: Dict[str, Any]
    created_at: datetime
    version: str = "v1"
    
    # Optional derived fields
    human_brief: Optional[str] = None
    synthetic_abstract: Optional[str] = None
    
    class Config:
        from_attributes = True