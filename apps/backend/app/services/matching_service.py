from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.core.config import settings
from app.schemas.matching import MatchRequest, MatchResult
from app.services.external_apis import ExternalAPIService

class MatchingService:
    """Service for matching patients to specialists based on case analysis."""
    
    def __init__(self, db: Session):
        self.db = db
        self.qdrant_client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        self.external_api_service = ExternalAPIService()
    
    async def find_matches(self, match_request: MatchRequest) -> List[MatchResult]:
        """
        Find specialist matches for a given case using hybrid retrieval.
        """
        case_json = match_request.case_json
        
        # Step 1: Vector search using synthetic abstract
        vector_results = await self._vector_search(case_json)
        
        # Step 2: Symbolic filtering
        filtered_results = await self._apply_symbolic_filters(
            vector_results, 
            match_request.filters
        )
        
        # Step 3: Aggregate to doctors
        doctor_works = await self._aggregate_to_doctors(filtered_results)
        
        # Step 4: Calculate scores
        scored_doctors = await self._calculate_scores(doctor_works, case_json)
        
        # Step 5: Generate evidence and explanations
        matches = await self._generate_match_results(scored_doctors, case_json)
        
        # Return top matches
        return sorted(matches, key=lambda x: x.total_score, reverse=True)[:10]
    
    async def _vector_search(self, case_json: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform vector search against works collection."""
        
        # Generate synthetic abstract for embedding
        from app.services.case_parser import CaseParserService
        parser = CaseParserService()
        synthetic_abstract = parser.generate_synthetic_abstract(case_json)
        
        # TODO: Generate embedding using sentence transformer
        # For now, return mock results
        
        try:
            # Search in works_vectors collection
            search_result = self.qdrant_client.search(
                collection_name="works_vectors",
                query_vector=[0.1] * 768,  # Mock embedding
                limit=100,
                score_threshold=0.7
            )
            
            return [
                {
                    "work_id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                }
                for hit in search_result
            ]
            
        except Exception as e:
            # Return mock data if Qdrant is not available
            return self._get_mock_vector_results()
    
    async def _apply_symbolic_filters(
        self, 
        vector_results: List[Dict[str, Any]], 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Apply symbolic filters to vector search results."""
        
        if not filters:
            filters = {}
        
        filtered = []
        
        for result in vector_results:
            payload = result.get("payload", {})
            
            # Year filter
            min_year = filters.get("min_year", 2019)
            if payload.get("year", 2025) < min_year:
                continue
            
            # MeSH terms filter
            required_mesh = filters.get("mesh_terms", [])
            result_mesh = payload.get("mesh_terms", [])
            if required_mesh and not any(term in result_mesh for term in required_mesh):
                continue
            
            # Geography filter
            allowed_countries = filters.get("countries", [])
            if allowed_countries and payload.get("country") not in allowed_countries:
                continue
            
            # Specialty filter
            required_specialties = filters.get("specialties", [])
            if required_specialties:
                # TODO: Check doctor specialty
                pass
            
            filtered.append(result)
        
        return filtered
    
    async def _aggregate_to_doctors(self, works: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Aggregate works by doctor_id."""
        
        doctor_works = {}
        
        for work in works:
            # TODO: Query database to get doctor_ids for this work
            # For now, use mock data
            mock_doctors = [f"doctor_{i}" for i in range(1, 4)]
            
            for doctor_id in mock_doctors:
                if doctor_id not in doctor_works:
                    doctor_works[doctor_id] = []
                doctor_works[doctor_id].append(work)
        
        return doctor_works
    
    async def _calculate_scores(
        self, 
        doctor_works: Dict[str, List[Dict[str, Any]]], 
        case_json: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Calculate scores for each doctor based on the scoring formula."""
        
        scored_doctors = []
        
        for doctor_id, works in doctor_works.items():
            # Calculate components
            components = await self._calculate_score_components(doctor_id, works, case_json)
            
            # Apply scoring formula
            doctor_score = (
                2 * components["pubs_5y"] + 
                5 * components["trials_pi"] + 
                1 * components["citations_bucket"]
            )
            
            institution_score = (
                0.5 * components["inst_pubs"] + 
                2 * components["inst_trials"] + 
                0.5 * components["nih_grants"]
            )
            
            total_score = doctor_score + 0.5 * institution_score
            
            scored_doctors.append({
                "doctor_id": doctor_id,
                "doctor_score": doctor_score,
                "institution_score": institution_score,
                "total_score": total_score,
                "components": components,
                "works": works
            })
        
        return scored_doctors
    
    async def _calculate_score_components(
        self, 
        doctor_id: str, 
        works: List[Dict[str, Any]], 
        case_json: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate individual scoring components for a doctor."""
        
        current_year = 2025
        
        # Publications in last 5 years
        pubs_5y = len([
            w for w in works 
            if w.get("payload", {}).get("source") == "pubmed" and 
               w.get("payload", {}).get("year", 0) >= (current_year - 5)
        ])
        
        # Clinical trials as PI
        trials_pi = len([
            w for w in works 
            if w.get("payload", {}).get("source") == "ctgov" and 
               w.get("payload", {}).get("is_pi", False)
        ])
        
        # Citations bucket (simplified)
        citations_bucket = min(3, pubs_5y // 5)  # Max 3 points, 1 per 5 pubs
        
        # Institution metrics (TODO: query from affiliations)
        inst_pubs = pubs_5y * 5  # Mock: assume institution has 5x doctor's pubs
        inst_trials = trials_pi * 2  # Mock: assume institution has 2x doctor's trials
        nih_grants = trials_pi  # Mock: assume grants correlate with trials
        
        return {
            "pubs_5y": pubs_5y,
            "trials_pi": trials_pi,
            "citations_bucket": citations_bucket,
            "inst_pubs": inst_pubs,
            "inst_trials": inst_trials,
            "nih_grants": nih_grants
        }
    
    async def _generate_match_results(
        self, 
        scored_doctors: List[Dict[str, Any]], 
        case_json: Dict[str, Any]
    ) -> List[MatchResult]:
        """Generate final match results with evidence."""
        
        matches = []
        
        for doctor_data in scored_doctors:
            # Generate evidence from works
            evidence = self._generate_evidence(doctor_data["works"])
            
            # TODO: Query database for doctor details
            doctor_info = self._get_mock_doctor_info(doctor_data["doctor_id"])
            
            match_result = MatchResult(
                doctor_id=doctor_data["doctor_id"],
                doctor_name=doctor_info["name"],
                institution=doctor_info["institution"],
                specialty=doctor_info["specialty"],
                total_score=doctor_data["total_score"],
                doctor_score=doctor_data["doctor_score"],
                institution_score=doctor_data["institution_score"],
                components=doctor_data["components"],
                evidence=evidence,
                explanation=self._generate_explanation(doctor_data, case_json)
            )
            
            matches.append(match_result)
        
        return matches
    
    def _generate_evidence(self, works: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate evidence list from works."""
        
        evidence = []
        
        for work in works[:5]:  # Top 5 pieces of evidence
            payload = work.get("payload", {})
            
            evidence_item = {
                "type": payload.get("source", "unknown"),
                "title": payload.get("title", "Untitled"),
                "year": payload.get("year"),
                "url": payload.get("url"),
                "relevance_score": work.get("score", 0)
            }
            
            # Add type-specific fields
            if payload.get("source") == "pubmed":
                evidence_item["pmid"] = payload.get("source_key")
            elif payload.get("source") == "ctgov":
                evidence_item["nct_id"] = payload.get("source_key")
                evidence_item["role"] = "PI" if payload.get("is_pi") else "Investigator"
            elif payload.get("source") == "nih_reporter":
                evidence_item["project_id"] = payload.get("source_key")
            
            evidence.append(evidence_item)
        
        return evidence
    
    def _generate_explanation(
        self, 
        doctor_data: Dict[str, Any], 
        case_json: Dict[str, Any]
    ) -> str:
        """Generate human-readable explanation of the match."""
        
        components = doctor_data["components"]
        condition = case_json["condition"]["text"]
        
        explanation_parts = []
        
        if components["pubs_5y"] > 0:
            explanation_parts.append(
                f"{components['pubs_5y']} recent publications related to {condition}"
            )
        
        if components["trials_pi"] > 0:
            explanation_parts.append(
                f"Principal investigator on {components['trials_pi']} clinical trials"
            )
        
        if components["inst_pubs"] > 10:
            explanation_parts.append(
                f"Institution has strong research presence with {components['inst_pubs']} related publications"
            )
        
        if not explanation_parts:
            explanation_parts.append("Matched based on vector similarity to case description")
        
        return ". ".join(explanation_parts) + "."
    
    def _get_mock_vector_results(self) -> List[Dict[str, Any]]:
        """Return mock vector search results for development."""
        
        return [
            {
                "work_id": f"work_{i}",
                "score": 0.9 - (i * 0.1),
                "payload": {
                    "source": "pubmed",
                    "source_key": f"PMID{12345000 + i}",
                    "title": f"Study on Critical Limb Ischemia Treatment {i+1}",
                    "year": 2023 - (i % 5),
                    "mesh_terms": ["D016491", "D058729"],
                    "author_ids": [f"doctor_{(i % 3) + 1}"],
                    "institution_ids": [f"inst_{(i % 2) + 1}"],
                    "country": "US",
                    "is_pi": i % 3 == 0
                }
            }
            for i in range(20)
        ]
    
    def _get_mock_doctor_info(self, doctor_id: str) -> Dict[str, Any]:
        """Return mock doctor information."""
        
        mock_doctors = {
            "doctor_1": {
                "name": "Dr. Sarah Johnson",
                "institution": "Cleveland Clinic",
                "specialty": "Vascular Surgery"
            },
            "doctor_2": {
                "name": "Dr. Michael Chen",
                "institution": "Mayo Clinic",
                "specialty": "Interventional Cardiology"
            },
            "doctor_3": {
                "name": "Dr. Emily Rodriguez",
                "institution": "Johns Hopkins",
                "specialty": "Vascular Surgery"
            }
        }
        
        return mock_doctors.get(doctor_id, {
            "name": f"Dr. Unknown ({doctor_id})",
            "institution": "Unknown Institution",
            "specialty": "Unknown Specialty"
        })