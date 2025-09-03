from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import uuid

class MatchFilters(BaseModel):
    min_year: Optional[int] = 2019
    mesh_terms: Optional[List[str]] = None
    specialties: Optional[List[str]] = None
    countries: Optional[List[str]] = None
    institutions: Optional[List[str]] = None
    max_distance_miles: Optional[float] = None
    min_publications: Optional[int] = None
    min_trials: Optional[int] = None

class MatchRequest(BaseModel):
    case_json: Dict[str, Any]
    filters: Optional[MatchFilters] = None
    max_results: Optional[int] = 10
    explanation_level: Optional[str] = "standard"  # "brief", "standard", "detailed"

class MatchEvidence(BaseModel):
    type: str  # "pubmed", "ctgov", "nih_reporter", "crossref", "openalex"
    title: str
    year: Optional[int] = None
    url: Optional[str] = None
    relevance_score: Optional[float] = None
    
    # Type-specific fields
    pmid: Optional[str] = None
    nct_id: Optional[str] = None
    project_id: Optional[str] = None
    doi: Optional[str] = None
    role: Optional[str] = None  # For trials/grants

class MatchScoreComponents(BaseModel):
    pubs_5y: int = 0
    trials_pi: int = 0
    citations_bucket: int = 0
    inst_pubs: int = 0
    inst_trials: int = 0
    nih_grants: int = 0

class MatchResult(BaseModel):
    doctor_id: str
    doctor_name: str
    institution: str
    specialty: Optional[str] = None
    
    # Scores
    total_score: float
    doctor_score: float
    institution_score: float
    components: MatchScoreComponents
    
    # Evidence and explanation
    evidence: List[MatchEvidence]
    explanation: str
    
    # Additional context
    location: Optional[str] = None
    years_experience: Optional[int] = None
    board_certifications: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    
    # Contact info (for approved matches)
    contact_info: Optional[Dict[str, Any]] = None

class MatchApproval(BaseModel):
    case_id: str
    doctor_id: str
    approved_by: str  # Navigator user ID
    notes: Optional[str] = None
    priority: Optional[int] = 1  # 1 = highest priority

class MatchDelivery(BaseModel):
    case_id: str
    approved_matches: List[MatchApproval]
    delivery_method: str  # "email", "portal", "both"
    include_case_brief: bool = True
    custom_message: Optional[str] = None

class ScoringExplanation(BaseModel):
    doctor_id: str
    case_id: str
    total_score: float
    breakdown: Dict[str, Any]
    evidence_details: List[Dict[str, Any]]
    methodology: str
    confidence_level: str  # "high", "medium", "low"