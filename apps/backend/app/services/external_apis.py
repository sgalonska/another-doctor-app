import httpx
import asyncio
from typing import Dict, List, Any, Optional
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

from app.core.config import settings

class ExternalAPIService:
    """Service for interacting with external medical research APIs."""
    
    def __init__(self):
        self.session = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": f"another-doctor/1.0 (mailto:{settings.CROSSREF_EMAIL})"
            }
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()

class PubMedAPI(ExternalAPIService):
    """PubMed/Entrez API client for biomedical publications."""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    async def search_publications(
        self, 
        query: str, 
        max_results: int = 50,
        sort: str = "pub_date",
        min_date: Optional[str] = None,
        max_date: Optional[str] = None
    ) -> List[str]:
        """Search PubMed for publications and return PMIDs."""
        
        params = {
            "db": "pubmed",
            "retmode": "json",
            "retmax": max_results,
            "sort": sort,
            "term": query
        }
        
        if min_date and max_date:
            params["datetype"] = "pdat"
            params["mindate"] = min_date
            params["maxdate"] = max_date
        
        if settings.PUBMED_API_KEY:
            params["api_key"] = settings.PUBMED_API_KEY
        
        try:
            response = await self.session.get(
                f"{self.BASE_URL}/esearch.fcgi",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("esearchresult", {}).get("idlist", [])
            
        except Exception as e:
            print(f"PubMed search error: {e}")
            return []
    
    async def fetch_publication_details(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """Fetch detailed information for a list of PMIDs."""
        
        if not pmids:
            return []
        
        params = {
            "db": "pubmed",
            "retmode": "xml",
            "id": ",".join(pmids[:200])  # Max 200 IDs per request
        }
        
        if settings.PUBMED_API_KEY:
            params["api_key"] = settings.PUBMED_API_KEY
        
        try:
            response = await self.session.get(
                f"{self.BASE_URL}/efetch.fcgi",
                params=params
            )
            response.raise_for_status()
            
            return self._parse_pubmed_xml(response.text)
            
        except Exception as e:
            print(f"PubMed fetch error: {e}")
            return []
    
    def _parse_pubmed_xml(self, xml_text: str) -> List[Dict[str, Any]]:
        """Parse PubMed XML response into structured data."""
        
        publications = []
        
        try:
            root = ET.fromstring(xml_text)
            
            for article in root.findall(".//PubmedArticle"):
                pub = self._extract_publication_data(article)
                if pub:
                    publications.append(pub)
                    
        except ET.ParseError as e:
            print(f"XML parsing error: {e}")
        
        return publications
    
    def _extract_publication_data(self, article_element) -> Optional[Dict[str, Any]]:
        """Extract publication data from XML element."""
        
        try:
            # Basic article info
            medline_citation = article_element.find("MedlineCitation")
            pmid = medline_citation.find("PMID").text
            
            article = medline_citation.find("Article")
            title = article.find("ArticleTitle").text or ""
            
            # Abstract
            abstract_element = article.find("Abstract/AbstractText")
            abstract = abstract_element.text if abstract_element is not None else ""
            
            # Publication date
            pub_date = article.find("Journal/JournalIssue/PubDate")
            year = None
            if pub_date is not None:
                year_elem = pub_date.find("Year")
                if year_elem is not None:
                    year = int(year_elem.text)
            
            # Authors
            authors = []
            author_list = article.find("AuthorList")
            if author_list is not None:
                for author in author_list.findall("Author"):
                    lastname = author.find("LastName")
                    forename = author.find("ForeName")
                    if lastname is not None and forename is not None:
                        authors.append(f"{forename.text} {lastname.text}")
            
            # MeSH terms
            mesh_terms = []
            mesh_list = medline_citation.find("MeshHeadingList")
            if mesh_list is not None:
                for mesh_heading in mesh_list.findall("MeshHeading"):
                    descriptor = mesh_heading.find("DescriptorName")
                    if descriptor is not None:
                        mesh_terms.append(descriptor.text)
            
            # Journal info
            journal = article.find("Journal/Title")
            journal_title = journal.text if journal is not None else ""
            
            # DOI
            doi = None
            article_id_list = article_element.find("PubmedData/ArticleIdList")
            if article_id_list is not None:
                for article_id in article_id_list.findall("ArticleId"):
                    if article_id.get("IdType") == "doi":
                        doi = article_id.text
                        break
            
            return {
                "source": "pubmed",
                "source_key": pmid,
                "title": title,
                "abstract": abstract,
                "year": year,
                "doi": doi,
                "authors": authors,
                "journal": journal_title,
                "mesh_terms": mesh_terms,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            }
            
        except Exception as e:
            print(f"Error extracting publication data: {e}")
            return None

class OpenAlexAPI(ExternalAPIService):
    """OpenAlex API client for academic works and authors."""
    
    BASE_URL = "https://api.openalex.org"
    
    async def search_works(
        self,
        query: str,
        per_page: int = 25,
        sort: str = "publication_year:desc",
        filter_params: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """Search OpenAlex for academic works."""
        
        params = {
            "search": query,
            "per_page": per_page,
            "sort": sort
        }
        
        if filter_params:
            for key, value in filter_params.items():
                params[f"filter[{key}]"] = value
        
        try:
            response = await self.session.get(
                f"{self.BASE_URL}/works",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            works = []
            
            for work in data.get("results", []):
                processed_work = self._process_openalex_work(work)
                if processed_work:
                    works.append(processed_work)
            
            return works
            
        except Exception as e:
            print(f"OpenAlex search error: {e}")
            return []
    
    def _process_openalex_work(self, work: Dict[str, Any]) -> Dict[str, Any]:
        """Process OpenAlex work data into standardized format."""
        
        # Extract authors and institutions
        authors = []
        institutions = []
        
        for authorship in work.get("authorships", []):
            author = authorship.get("author", {})
            if author.get("display_name"):
                authors.append(author["display_name"])
            
            for institution in authorship.get("institutions", []):
                if institution.get("display_name"):
                    institutions.append(institution["display_name"])
        
        # Extract concepts (similar to MeSH terms)
        concepts = [
            concept["display_name"] 
            for concept in work.get("concepts", [])
            if concept.get("score", 0) > 0.3  # Only high-confidence concepts
        ]
        
        return {
            "source": "openalex",
            "source_key": work.get("id", "").replace("https://openalex.org/", ""),
            "title": work.get("title", ""),
            "abstract": work.get("abstract", ""),
            "year": work.get("publication_year"),
            "doi": work.get("doi", "").replace("https://doi.org/", "") if work.get("doi") else None,
            "authors": authors,
            "institutions": list(set(institutions)),  # Remove duplicates
            "concepts": concepts,
            "citation_count": work.get("cited_by_count", 0),
            "url": work.get("id", "")
        }

class ClinicalTrialsAPI(ExternalAPIService):
    """ClinicalTrials.gov API client."""
    
    BASE_URL = "https://clinicaltrials.gov/api"
    
    async def search_studies(
        self,
        search_terms: str,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """Search ClinicalTrials.gov for studies."""
        
        params = {
            "expr": search_terms,
            "min_rnk": 1,
            "max_rnk": max_results,
            "fmt": "json"
        }
        
        try:
            response = await self.session.get(
                f"{self.BASE_URL}/query/full_studies",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            studies = []
            
            full_studies = data.get("FullStudiesResponse", {}).get("FullStudies", [])
            for study_wrapper in full_studies:
                study = study_wrapper.get("Study", {})
                processed_study = self._process_clinical_trial(study)
                if processed_study:
                    studies.append(processed_study)
            
            return studies
            
        except Exception as e:
            print(f"ClinicalTrials.gov search error: {e}")
            return []
    
    def _process_clinical_trial(self, study: Dict[str, Any]) -> Dict[str, Any]:
        """Process clinical trial data into standardized format."""
        
        protocol_section = study.get("ProtocolSection", {})
        identification_module = protocol_section.get("IdentificationModule", {})
        description_module = protocol_section.get("DescriptionModule", {})
        status_module = protocol_section.get("StatusModule", {})
        
        # Extract investigators
        investigators = []
        contacts_locations = protocol_section.get("ContactsLocationsModule", {})
        if contacts_locations:
            overall_officials = contacts_locations.get("OverallOfficialList", {}).get("OverallOfficial", [])
            for official in overall_officials:
                name = official.get("OverallOfficialName", "")
                role = official.get("OverallOfficialRole", "")
                affiliation = official.get("OverallOfficialAffiliation", "")
                
                investigators.append({
                    "name": name,
                    "role": role,
                    "affiliation": affiliation,
                    "is_pi": "principal investigator" in role.lower()
                })
        
        # Extract conditions
        conditions_module = protocol_section.get("ConditionsModule", {})
        conditions = conditions_module.get("ConditionList", {}).get("Condition", [])
        
        return {
            "source": "ctgov",
            "source_key": identification_module.get("NCTId", ""),
            "title": identification_module.get("BriefTitle", ""),
            "abstract": description_module.get("BriefSummary", {}).get("BriefSummaryText", ""),
            "year": self._extract_year_from_date(status_module.get("StartDateStruct", {}).get("StartDate", "")),
            "status": status_module.get("OverallStatus", ""),
            "conditions": conditions,
            "investigators": investigators,
            "phase": protocol_section.get("DesignModule", {}).get("PhaseList", {}).get("Phase", []),
            "url": f"https://clinicaltrials.gov/ct2/show/{identification_module.get('NCTId', '')}"
        }
    
    def _extract_year_from_date(self, date_str: str) -> Optional[int]:
        """Extract year from date string."""
        if not date_str:
            return None
        
        try:
            # Handle various date formats
            if len(date_str) >= 4 and date_str[:4].isdigit():
                return int(date_str[:4])
        except (ValueError, IndexError):
            pass
        
        return None

class NIHReporterAPI(ExternalAPIService):
    """NIH RePORTER API client for grant information."""
    
    BASE_URL = "https://api.reporter.nih.gov/v2"
    
    async def search_projects(
        self,
        search_terms: str,
        limit: int = 25,
        fiscal_years: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """Search NIH RePORTER for research projects."""
        
        criteria = {
            "text_phrase": search_terms
        }
        
        if fiscal_years:
            criteria["fiscal_years"] = fiscal_years
        
        payload = {
            "criteria": criteria,
            "include_fields": [
                "ProjectNum", "ProjectTitle", "AbstractText", "FiscalYear",
                "PrincipalInvestigators", "Organization", "ContactPi"
            ],
            "limit": limit
        }
        
        try:
            response = await self.session.post(
                f"{self.BASE_URL}/projects/search",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            projects = []
            
            for project in data.get("results", []):
                processed_project = self._process_nih_project(project)
                if processed_project:
                    projects.append(processed_project)
            
            return projects
            
        except Exception as e:
            print(f"NIH RePORTER search error: {e}")
            return []
    
    def _process_nih_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Process NIH project data into standardized format."""
        
        # Extract PI information
        pi_info = {}
        contact_pi = project.get("ContactPi", {})
        if contact_pi:
            pi_info = {
                "name": f"{contact_pi.get('FirstName', '')} {contact_pi.get('LastName', '')}".strip(),
                "email": contact_pi.get("Email", "")
            }
        
        # Extract organization
        org = project.get("Organization", {})
        organization = f"{org.get('OrgName', '')} ({org.get('OrgCity', '')}, {org.get('OrgStateCode', '')})".strip(" ()")
        
        return {
            "source": "nih_reporter",
            "source_key": project.get("ProjectNum", ""),
            "title": project.get("ProjectTitle", ""),
            "abstract": project.get("AbstractText", ""),
            "year": project.get("FiscalYear"),
            "pi": pi_info,
            "organization": organization,
            "url": f"https://reporter.nih.gov/project-details/{project.get('ProjectNum', '')}"
        }

class CrossrefAPI(ExternalAPIService):
    """Crossref API client for DOI metadata."""
    
    BASE_URL = "https://api.crossref.org"
    
    async def search_works(
        self,
        query: str,
        rows: int = 25,
        sort: str = "issued",
        order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """Search Crossref for academic works."""
        
        params = {
            "query": query,
            "rows": rows,
            "sort": sort,
            "order": order
        }
        
        try:
            response = await self.session.get(
                f"{self.BASE_URL}/works",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            works = []
            
            for item in data.get("message", {}).get("items", []):
                processed_work = self._process_crossref_work(item)
                if processed_work:
                    works.append(processed_work)
            
            return works
            
        except Exception as e:
            print(f"Crossref search error: {e}")
            return []
    
    def _process_crossref_work(self, work: Dict[str, Any]) -> Dict[str, Any]:
        """Process Crossref work data into standardized format."""
        
        # Extract authors
        authors = []
        for author in work.get("author", []):
            given = author.get("given", "")
            family = author.get("family", "")
            if given and family:
                authors.append(f"{given} {family}")
        
        # Extract publication year
        year = None
        published = work.get("published-print", work.get("published-online", {}))
        if published and "date-parts" in published:
            date_parts = published["date-parts"][0]
            if date_parts and len(date_parts) > 0:
                year = date_parts[0]
        
        # Extract journal
        journal = ""
        container_title = work.get("container-title", [])
        if container_title:
            journal = container_title[0]
        
        return {
            "source": "crossref",
            "source_key": work.get("DOI", ""),
            "title": work.get("title", [""])[0],
            "abstract": work.get("abstract", ""),
            "year": year,
            "doi": work.get("DOI", ""),
            "authors": authors,
            "journal": journal,
            "type": work.get("type", ""),
            "url": work.get("URL", f"https://doi.org/{work.get('DOI', '')}")
        }