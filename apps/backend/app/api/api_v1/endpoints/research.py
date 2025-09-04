"""
Research aggregation endpoints
"""
from typing import List, Optional, Any
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from app.services.research_aggregator import research_aggregator, AggregatedResults

router = APIRouter()

class ResearchQuery(BaseModel):
    query: str
    max_results_per_source: int = 25
    include_sources: Optional[List[str]] = None

class ResearchResponse(BaseModel):
    query: str
    total_results: int
    sources_queried: List[str]
    execution_time_ms: int
    results: dict
    errors: List[str]

@router.get("/search", response_model=ResearchResponse)
async def search_all_research_sources(
    q: str = Query(..., description="Search query"),
    max_results: int = Query(25, ge=1, le=100, description="Max results per source"),
    sources: Optional[str] = Query(None, description="Comma-separated list of sources: pubmed,openalex,clinical_trials,nih_reporter,crossref")
) -> Any:
    """
    Search all research sources and return aggregated results
    
    Available sources:
    - pubmed: PubMed biomedical publications
    - openalex: OpenAlex academic works
    - crossref: Crossref DOI metadata
    - clinical_trials: ClinicalTrials.gov studies
    - nih_reporter: NIH grant projects
    """
    try:
        include_sources = sources.split(',') if sources else None
        
        async with research_aggregator:
            results = await research_aggregator.search_all_sources(
                query=q,
                max_results_per_source=max_results,
                include_sources=include_sources
            )
        
        return ResearchResponse(**results.to_dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/publications")
async def search_publications_only(
    q: str = Query(..., description="Search query"),
    max_results: int = Query(50, ge=1, le=200, description="Maximum results")
) -> Any:
    """
    Search only publication sources (PubMed, OpenAlex, Crossref)
    """
    try:
        async with research_aggregator:
            results = await research_aggregator.search_publications_only(
                query=q,
                max_results=max_results
            )
        
        return {
            "query": q,
            "total_results": len(results),
            "publications": [result.to_dict() for result in results]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clinical-trials")
async def search_clinical_trials_only(
    q: str = Query(..., description="Search query"),
    max_results: int = Query(25, ge=1, le=100, description="Maximum results")
) -> Any:
    """
    Search only ClinicalTrials.gov
    """
    try:
        async with research_aggregator:
            results = await research_aggregator.search_clinical_trials_only(
                query=q,
                max_results=max_results
            )
        
        return {
            "query": q,
            "total_results": len(results),
            "clinical_trials": [result.to_dict() for result in results]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/grants")
async def search_grants_only(
    q: str = Query(..., description="Search query"),
    max_results: int = Query(25, ge=1, le=100, description="Maximum results")
) -> Any:
    """
    Search only NIH RePORTER grants
    """
    try:
        async with research_aggregator:
            results = await research_aggregator.search_grants_only(
                query=q,
                max_results=max_results
            )
        
        return {
            "query": q,
            "total_results": len(results),
            "grants": [result.to_dict() for result in results]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=ResearchResponse)
async def search_research_advanced(research_query: ResearchQuery) -> Any:
    """
    Advanced research search with POST body
    """
    try:
        async with research_aggregator:
            results = await research_aggregator.search_all_sources(
                query=research_query.query,
                max_results_per_source=research_query.max_results_per_source,
                include_sources=research_query.include_sources
            )
        
        return ResearchResponse(**results.to_dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sources")
async def get_available_sources() -> Any:
    """
    Get list of available research sources and their descriptions
    """
    return {
        "sources": {
            "pubmed": {
                "name": "PubMed",
                "description": "Biomedical literature database",
                "url": "https://pubmed.ncbi.nlm.nih.gov/",
                "data_types": ["publications", "abstracts", "mesh_terms"]
            },
            "openalex": {
                "name": "OpenAlex",
                "description": "Open catalog of scholarly papers, authors, and institutions",
                "url": "https://openalex.org/",
                "data_types": ["publications", "authors", "institutions", "citations"]
            },
            "crossref": {
                "name": "Crossref",
                "description": "DOI registration and metadata",
                "url": "https://www.crossref.org/",
                "data_types": ["publications", "doi", "journal_metadata"]
            },
            "clinical_trials": {
                "name": "ClinicalTrials.gov",
                "description": "Database of clinical studies",
                "url": "https://clinicaltrials.gov/",
                "data_types": ["clinical_trials", "investigators", "conditions"]
            },
            "nih_reporter": {
                "name": "NIH RePORTER",
                "description": "NIH research project database",
                "url": "https://reporter.nih.gov/",
                "data_types": ["grants", "principal_investigators", "organizations"]
            }
        }
    }