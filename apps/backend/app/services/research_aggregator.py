"""
Research Aggregation Service - Queries multiple APIs and combines results
"""
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

from app.services.external_apis import (
    PubMedAPI, 
    OpenAlexAPI, 
    ClinicalTrialsAPI, 
    NIHReporterAPI, 
    CrossrefAPI
)

logger = logging.getLogger(__name__)

@dataclass
class ResearchResult:
    """Unified research result structure"""
    source: str
    source_key: str
    title: str
    abstract: str
    year: Optional[int]
    authors: List[str]
    url: str
    relevance_score: float = 0.0
    additional_data: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class AggregatedResults:
    """Combined results from all research sources"""
    query: str
    total_results: int
    sources_queried: List[str]
    execution_time_ms: int
    publications: List[ResearchResult]
    clinical_trials: List[ResearchResult]
    grants: List[ResearchResult]
    errors: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "total_results": self.total_results,
            "sources_queried": self.sources_queried,
            "execution_time_ms": self.execution_time_ms,
            "results": {
                "publications": [pub.to_dict() for pub in self.publications],
                "clinical_trials": [trial.to_dict() for trial in self.clinical_trials], 
                "grants": [grant.to_dict() for grant in self.grants]
            },
            "errors": self.errors or []
        }

class ResearchAggregationService:
    """Service that aggregates research data from multiple external APIs"""
    
    def __init__(self):
        self.apis = {
            'pubmed': PubMedAPI(),
            'openalex': OpenAlexAPI(),
            'clinical_trials': ClinicalTrialsAPI(),
            'nih_reporter': NIHReporterAPI(),
            'crossref': CrossrefAPI()
        }
        
    async def search_all_sources(
        self,
        query: str,
        max_results_per_source: int = 25,
        include_sources: Optional[List[str]] = None
    ) -> AggregatedResults:
        """
        Search all available research sources and aggregate results
        
        Args:
            query: Search terms
            max_results_per_source: Maximum results per API
            include_sources: List of sources to include (if None, includes all)
        
        Returns:
            AggregatedResults object with combined data from all sources
        """
        start_time = datetime.now()
        
        # Determine which sources to query
        sources_to_query = include_sources if include_sources else list(self.apis.keys())
        errors = []
        
        # Create search tasks for each API
        tasks = []
        for source in sources_to_query:
            if source in self.apis:
                task = self._search_source(source, query, max_results_per_source)
                tasks.append((source, task))
        
        # Execute all searches concurrently
        results = {}
        async with asyncio.TaskGroup() as tg:
            task_results = {}
            for source, task in tasks:
                task_results[source] = tg.create_task(task)
        
        # Collect results and handle errors
        for source, task_result in task_results.items():
            try:
                results[source] = task_result.result()
            except Exception as e:
                logger.error(f"Error querying {source}: {e}")
                errors.append(f"{source}: {str(e)}")
                results[source] = []
        
        # Process and categorize results
        publications = []
        clinical_trials = []
        grants = []
        
        # Process PubMed results
        if 'pubmed' in results:
            publications.extend([
                self._convert_to_research_result(item, 'pubmed')
                for item in results['pubmed']
            ])
        
        # Process OpenAlex results  
        if 'openalex' in results:
            publications.extend([
                self._convert_to_research_result(item, 'openalex')
                for item in results['openalex']
            ])
        
        # Process Crossref results
        if 'crossref' in results:
            publications.extend([
                self._convert_to_research_result(item, 'crossref')
                for item in results['crossref']
            ])
        
        # Process Clinical Trials results
        if 'clinical_trials' in results:
            clinical_trials.extend([
                self._convert_to_research_result(item, 'clinical_trials')
                for item in results['clinical_trials']
            ])
        
        # Process NIH Reporter results
        if 'nih_reporter' in results:
            grants.extend([
                self._convert_to_research_result(item, 'nih_reporter')
                for item in results['nih_reporter']
            ])
        
        # Calculate relevance scores and sort
        publications = self._rank_results(publications, query)
        clinical_trials = self._rank_results(clinical_trials, query)
        grants = self._rank_results(grants, query)
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Create aggregated results
        total_results = len(publications) + len(clinical_trials) + len(grants)
        
        return AggregatedResults(
            query=query,
            total_results=total_results,
            sources_queried=sources_to_query,
            execution_time_ms=int(execution_time),
            publications=publications,
            clinical_trials=clinical_trials,
            grants=grants,
            errors=errors
        )
    
    async def search_publications_only(
        self,
        query: str,
        max_results: int = 50
    ) -> List[ResearchResult]:
        """Search only publication sources (PubMed, OpenAlex, Crossref)"""
        
        result = await self.search_all_sources(
            query=query,
            max_results_per_source=max_results // 3,
            include_sources=['pubmed', 'openalex', 'crossref']
        )
        
        return result.publications
    
    async def search_clinical_trials_only(
        self,
        query: str,
        max_results: int = 25
    ) -> List[ResearchResult]:
        """Search only clinical trials"""
        
        result = await self.search_all_sources(
            query=query,
            max_results_per_source=max_results,
            include_sources=['clinical_trials']
        )
        
        return result.clinical_trials
    
    async def search_grants_only(
        self,
        query: str,
        max_results: int = 25
    ) -> List[ResearchResult]:
        """Search only NIH grants"""
        
        result = await self.search_all_sources(
            query=query,
            max_results_per_source=max_results,
            include_sources=['nih_reporter']
        )
        
        return result.grants
    
    async def _search_source(
        self,
        source: str,
        query: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Search a single source"""
        
        try:
            api = self.apis[source]
            
            if source == 'pubmed':
                async with api:
                    pmids = await api.search_publications(query, max_results)
                    return await api.fetch_publication_details(pmids)
            
            elif source == 'openalex':
                async with api:
                    return await api.search_works(query, per_page=max_results)
            
            elif source == 'clinical_trials':
                async with api:
                    return await api.search_studies(query, max_results)
            
            elif source == 'nih_reporter':
                async with api:
                    return await api.search_projects(query, limit=max_results)
            
            elif source == 'crossref':
                async with api:
                    return await api.search_works(query, rows=max_results)
            
            return []
            
        except Exception as e:
            logger.error(f"Error searching {source}: {e}")
            return []
    
    def _convert_to_research_result(
        self,
        item: Dict[str, Any],
        source: str
    ) -> ResearchResult:
        """Convert API result to standardized ResearchResult"""
        
        additional_data = {}
        
        # Add source-specific additional data
        if source == 'pubmed':
            additional_data = {
                'mesh_terms': item.get('mesh_terms', []),
                'journal': item.get('journal', ''),
                'doi': item.get('doi')
            }
        elif source == 'openalex':
            additional_data = {
                'concepts': item.get('concepts', []),
                'institutions': item.get('institutions', []),
                'citation_count': item.get('citation_count', 0)
            }
        elif source == 'clinical_trials':
            additional_data = {
                'status': item.get('status', ''),
                'conditions': item.get('conditions', []),
                'investigators': item.get('investigators', []),
                'phase': item.get('phase', [])
            }
        elif source == 'nih_reporter':
            additional_data = {
                'pi': item.get('pi', {}),
                'organization': item.get('organization', '')
            }
        elif source == 'crossref':
            additional_data = {
                'journal': item.get('journal', ''),
                'type': item.get('type', ''),
                'doi': item.get('doi')
            }
        
        return ResearchResult(
            source=source,
            source_key=item.get('source_key', ''),
            title=item.get('title', ''),
            abstract=item.get('abstract', ''),
            year=item.get('year'),
            authors=item.get('authors', []),
            url=item.get('url', ''),
            additional_data=additional_data
        )
    
    def _rank_results(
        self,
        results: List[ResearchResult],
        query: str
    ) -> List[ResearchResult]:
        """Calculate relevance scores and sort results"""
        
        query_terms = query.lower().split()
        
        for result in results:
            score = 0.0
            
            # Score based on title relevance
            title_lower = result.title.lower()
            for term in query_terms:
                if term in title_lower:
                    score += 2.0
            
            # Score based on abstract relevance
            abstract_lower = result.abstract.lower()
            for term in query_terms:
                if term in abstract_lower:
                    score += 1.0
            
            # Boost recent publications
            if result.year and result.year >= 2020:
                score += 1.0
            elif result.year and result.year >= 2015:
                score += 0.5
            
            # Source-specific scoring
            if result.source == 'openalex' and result.additional_data:
                citation_count = result.additional_data.get('citation_count', 0)
                if citation_count > 100:
                    score += 2.0
                elif citation_count > 10:
                    score += 1.0
            
            result.relevance_score = score
        
        # Sort by relevance score (descending) and then by year (descending)
        return sorted(
            results,
            key=lambda x: (x.relevance_score, x.year or 0),
            reverse=True
        )
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Close all API connections
        for api in self.apis.values():
            if hasattr(api, '__aexit__'):
                await api.__aexit__(exc_type, exc_val, exc_tb)

# Global service instance
research_aggregator = ResearchAggregationService()