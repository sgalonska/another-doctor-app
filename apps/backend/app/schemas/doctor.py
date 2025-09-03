from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import uuid

class DoctorBase(BaseModel):
    full_name: str
    orcid: Optional[str] = None
    npi: Optional[str] = None
    primary_specialty: Optional[str] = None

class DoctorCreate(DoctorBase):
    pass

class DoctorUpdate(BaseModel):
    full_name: Optional[str] = None
    orcid: Optional[str] = None
    npi: Optional[str] = None
    primary_specialty: Optional[str] = None

class DoctorAffiliation(BaseModel):
    institution_name: str
    role: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

class DoctorPublication(BaseModel):
    source: str
    source_key: str
    title: str
    year: Optional[int] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    author_position: Optional[int] = None
    is_corresponding: Optional[bool] = None
    citation_count: Optional[int] = None

class DoctorTrial(BaseModel):
    source_key: str  # NCT ID
    title: str
    status: Optional[str] = None
    phase: Optional[List[str]] = None
    role: Optional[str] = None
    is_pi: Optional[bool] = None
    start_year: Optional[int] = None
    conditions: Optional[List[str]] = None

class DoctorGrant(BaseModel):
    source_key: str  # Project number
    title: str
    fiscal_year: Optional[int] = None
    role: str  # PI, Co-PI, etc.
    organization: Optional[str] = None
    amount: Optional[float] = None

class DoctorTopicScore(BaseModel):
    topic_name: str
    score: float
    components: Dict[str, Any]
    updated_at: datetime

class Doctor(DoctorBase):
    doctor_id: uuid.UUID
    created_at: datetime
    
    # Relationships (optional, loaded separately)
    affiliations: Optional[List[DoctorAffiliation]] = None
    recent_publications: Optional[List[DoctorPublication]] = None
    clinical_trials: Optional[List[DoctorTrial]] = None
    grants: Optional[List[DoctorGrant]] = None
    topic_scores: Optional[List[DoctorTopicScore]] = None
    
    class Config:
        from_attributes = True

class DoctorSearch(BaseModel):
    query: Optional[str] = None
    specialty: Optional[str] = None
    institution: Optional[str] = None
    location: Optional[str] = None
    min_publications: Optional[int] = None
    min_trials: Optional[int] = None