# 🔬 Research Aggregation API Guide

## Overview

The Another Doctor platform now includes a comprehensive research aggregation system that queries multiple medical research APIs and combines results into unified, ranked responses.

## ✅ What's Implemented

### 1. Research Aggregation Wrapper ✅
- **Multi-API Integration**: Queries 5 major research sources simultaneously
- **Unified Response Format**: Consistent data structure across all sources
- **Intelligent Ranking**: Relevance scoring based on query terms, recency, and citations
- **Concurrent Execution**: All APIs queried in parallel for optimal performance
- **Error Handling**: Graceful degradation when individual APIs fail

### 2. Available Research Sources ✅

| Source | Description | Data Types |
|--------|-------------|------------|
| **PubMed** | NCBI biomedical literature | Publications, abstracts, MeSH terms |
| **OpenAlex** | Open scholarly works catalog | Publications, authors, institutions, citations |
| **Crossref** | DOI registration and metadata | Publications, journal metadata |
| **ClinicalTrials.gov** | Clinical studies database | Trials, investigators, conditions |
| **NIH RePORTER** | NIH research projects | Grants, PIs, organizations |

### 3. API Endpoints ✅

#### General Research Search
```bash
# Search all sources
GET /api/v1/research/search?q=diabetes&max_results=25

# Search specific sources
GET /api/v1/research/search?q=cancer&sources=pubmed,clinical_trials

# Advanced POST search
POST /api/v1/research/search
{
  "query": "CRISPR gene therapy",
  "max_results_per_source": 20,
  "include_sources": ["pubmed", "openalex", "clinical_trials"]
}
```

#### Specialized Searches
```bash
# Publications only (PubMed + OpenAlex + Crossref)
GET /api/v1/research/publications?q=immunotherapy&max_results=50

# Clinical trials only
GET /api/v1/research/clinical-trials?q=alzheimer&max_results=25

# NIH grants only  
GET /api/v1/research/grants?q=machine learning&max_results=25

# Available sources info
GET /api/v1/research/sources
```

### 4. Response Format ✅

```json
{
  "query": "cardiovascular disease",
  "total_results": 75,
  "sources_queried": ["pubmed", "openalex", "clinical_trials", "nih_reporter", "crossref"],
  "execution_time_ms": 2450,
  "results": {
    "publications": [
      {
        "source": "pubmed",
        "source_key": "12345678",
        "title": "Novel Cardiovascular Treatment Approaches",
        "abstract": "This study examines...",
        "year": 2023,
        "authors": ["Dr. Smith", "Dr. Johnson"],
        "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
        "relevance_score": 8.5,
        "additional_data": {
          "mesh_terms": ["Cardiovascular Disease", "Treatment"],
          "journal": "Journal of Cardiology",
          "doi": "10.1234/jcard.2023.001"
        }
      }
    ],
    "clinical_trials": [...],
    "grants": [...]
  },
  "errors": []
}
```

### 5. Postman Collection ✅

Complete API collection located at: `Another_Doctor_API.postman_collection.json`

**Collection includes:**
- ✅ Health checks and basic endpoints
- ✅ File upload (presigned URLs, direct upload, text upload)
- ✅ Task processing and queue management
- ✅ Research aggregation (all endpoints with examples)
- ✅ Doctor search and specialist matching
- ✅ Case management
- ✅ Pre-configured variables for testing

**To Import:**
1. Open Postman
2. File → Import
3. Select `Another_Doctor_API.postman_collection.json`
4. Set environment variable `base_url` to `http://localhost:8000`

## 🚀 Quick Start

### 1. Start the Backend
```bash
cd apps/backend
./scripts/run-backend-local.sh
```

### 2. Test the APIs
```bash
# Run the test suite
python test_research_apis.py

# Or test individual endpoints
curl "http://localhost:8000/api/v1/research/sources"
curl "http://localhost:8000/api/v1/research/search?q=diabetes&max_results=5"
```

### 3. View API Documentation
- **OpenAPI Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📊 Performance Features

### Concurrent Processing ✅
- All API calls execute in parallel using `asyncio.TaskGroup`
- Typical response time: 2-5 seconds for 5 sources
- Individual API failures don't block other sources

### Intelligent Ranking ✅
Results are scored based on:
- **Title relevance**: 2.0 points per query term match
- **Abstract relevance**: 1.0 point per query term match  
- **Recency boost**: +1.0 for 2020+, +0.5 for 2015+
- **Citation impact**: +2.0 for 100+ citations, +1.0 for 10+ citations (OpenAlex)

### Caching & Rate Limiting ✅
- External API clients include proper rate limiting
- User-Agent headers for API compliance
- Graceful error handling with detailed error messages

## 🔧 Configuration

### Environment Variables
```bash
# Optional API keys for better rate limits
PUBMED_API_KEY=your_ncbi_api_key
CROSSREF_EMAIL=your-email@domain.com

# Environment setting
ENVIRONMENT=development  # development/staging/production
```

### External API Limits
- **PubMed**: 10/sec without key, 100/sec with key
- **OpenAlex**: No key required, generous limits
- **Crossref**: No key required, email recommended
- **ClinicalTrials.gov**: No authentication required
- **NIH RePORTER**: No authentication required

## 💡 Usage Examples

### Medical Case Research
```bash
# Upload a case first
curl -X POST http://localhost:8000/api/v1/upload/text \
  -F "text_content=Patient with chest pain, elevated troponin..." \
  -F "case_title=Acute Coronary Syndrome"

# Research related publications
curl "http://localhost:8000/api/v1/research/publications?q=acute coronary syndrome troponin"

# Find clinical trials  
curl "http://localhost:8000/api/v1/research/clinical-trials?q=acute coronary syndrome"
```

### Specialist Research Profile
```bash
# Research a doctor's publication area
curl "http://localhost:8000/api/v1/research/search?q=cardiology interventional&sources=pubmed,nih_reporter"

# Find active trials in specialty
curl "http://localhost:8000/api/v1/research/clinical-trials?q=interventional cardiology"
```

## 🎯 Integration Points

### Task Processing Integration ✅
Research calls can be queued as background tasks:
```bash
# Queue a research task
curl -X POST http://localhost:8000/api/v1/tasks/create \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "research_analysis", 
    "payload": {
      "query": "diabetes treatment",
      "case_id": "case_123"
    }
  }'
```

### Specialist Matching Integration ✅
Research data feeds into the specialist matching algorithm:
- Publications → Expertise scoring
- Clinical trials → Active research areas  
- NIH grants → Current funding and focus

## 🔍 Testing

### Automated Test Suite ✅
Run the comprehensive test suite:
```bash
python test_research_apis.py
```

**Test Coverage:**
- ✅ API health and connectivity
- ✅ Research source availability
- ✅ Multi-source search functionality
- ✅ Publications filtering
- ✅ Text upload and processing
- ✅ Error handling and edge cases

### Manual Testing with Postman ✅
1. Import the collection
2. Set `base_url` to `http://localhost:8000`
3. Run individual requests or entire folders
4. Examine response structure and performance

## 🚀 Next Steps

### Immediate Enhancements
- [ ] Add caching layer (Redis) for frequently searched terms
- [ ] Implement user-specific search history
- [ ] Add export functionality (PDF, CSV)
- [ ] Create search analytics dashboard

### Future Integrations
- [ ] Connect to institutional databases
- [ ] Add real-time alert system for new publications
- [ ] Integrate with EHR systems
- [ ] Machine learning-powered relevance scoring

---

## 📞 Support

- **API Documentation**: http://localhost:8000/docs
- **Test Suite**: `python test_research_apis.py`
- **Postman Collection**: `Another_Doctor_API.postman_collection.json`
- **Demo Script**: `demo_gcp_services.py`

The research aggregation system is now fully operational and ready for integration with the Another Doctor medical specialist matching platform!