# API Reference

Complete reference for the Another Doctor REST API endpoints.

## 📋 Base Information

- **Base URL**: `https://api.anotherdoctor.com` (production)
- **Dev URL**: `http://localhost:8000` (development)
- **API Version**: v1
- **Authentication**: Bearer token (JWT)
- **Content Type**: `application/json`

## 🚀 Quick Start

```bash
# Health check
curl http://localhost:8000/health

# Interactive docs (when running locally)
open http://localhost:8000/docs
```

## 📝 Cases API

### Upload Medical Text

**`POST /api/v1/upload/text`**

Upload medical text for case processing.

```bash
curl -X POST http://localhost:8000/api/v1/upload/text \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text_content=Patient has critical limb ischemia in left foot. Previous angioplasty failed." \
  -d "case_title=CLI Case 2024-001"
```

**Response:**
```json
{
  "case_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "processing"
}
```

### Create Case

**`POST /api/v1/cases`**

Create a new case from parsed medical data.

```bash
curl -X POST http://localhost:8000/api/v1/cases \
  -H "Content-Type: application/json" \
  -d '{
    "raw_text": "Patient presents with critical limb ischemia...",
    "title": "CLI Case",
    "patient_id": "patient123"
  }'
```

**Request Body:**
```json
{
  "raw_text": "string",
  "title": "string (optional)",
  "patient_id": "string (optional)"
}
```

**Response:**
```json
{
  "case_id": "123e4567-e89b-12d3-a456-426614174000",
  "casejson": {
    "condition": {
      "text": "critical limb ischemia",
      "icd10": "I70.25",
      "snomed": "443165006",
      "mesh": "D016491"
    },
    "anatomy": {
      "site": "foot",
      "laterality": "left"
    },
    "urgency": "high"
  },
  "created_at": "2024-09-03T15:30:00Z",
  "version": "v1"
}
```

### Get Case

**`GET /api/v1/cases/{case_id}`**

Retrieve a specific case by ID.

```bash
curl http://localhost:8000/api/v1/cases/123e4567-e89b-12d3-a456-426614174000
```

## 🔍 Matching API

### Find Specialist Matches

**`POST /api/v1/matching/match`**

Find specialist matches for a given case.

```bash
curl -X POST http://localhost:8000/api/v1/matching/match \
  -H "Content-Type: application/json" \
  -d '{
    "case_json": {
      "condition": {
        "text": "critical limb ischemia",
        "mesh": "D016491"
      },
      "anatomy": {
        "site": "foot",
        "laterality": "left"
      }
    },
    "filters": {
      "min_year": 2019,
      "max_results": 10
    }
  }'
```

**Request Body:**
```json
{
  "case_json": {
    "condition": { "text": "string", "mesh": "string" },
    "anatomy": { "site": "string", "laterality": "string" }
  },
  "filters": {
    "min_year": 2019,
    "mesh_terms": ["string"],
    "specialties": ["string"],
    "countries": ["string"],
    "max_results": 10
  }
}
```

**Response:**
```json
[
  {
    "doctor_id": "doc123",
    "doctor_name": "Dr. Sarah Johnson",
    "institution": "Cleveland Clinic",
    "specialty": "Vascular Surgery",
    "total_score": 27.5,
    "doctor_score": 18.0,
    "institution_score": 9.5,
    "components": {
      "pubs_5y": 6,
      "trials_pi": 2,
      "citations_bucket": 2,
      "inst_pubs": 45,
      "inst_trials": 8,
      "nih_grants": 3
    },
    "evidence": [
      {
        "type": "pubmed",
        "title": "Distal bypass for critical limb ischemia outcomes",
        "year": 2023,
        "pmid": "12345678",
        "relevance_score": 0.92
      },
      {
        "type": "ctgov", 
        "title": "Pedal Loop Revascularization Trial",
        "nct_id": "NCT01234567",
        "role": "PI"
      }
    ],
    "explanation": "6 recent publications related to critical limb ischemia. Principal investigator on 2 clinical trials."
  }
]
```

### Get Match Explanation

**`GET /api/v1/matching/scoring-explanation/{case_id}/{doctor_id}`**

Get detailed scoring explanation for a specific doctor-case match.

```bash
curl http://localhost:8000/api/v1/matching/scoring-explanation/case123/doctor456
```

## 👩‍⚕️ Doctors API

### Search Doctors

**`GET /api/v1/doctors/search`**

Search for doctors by various criteria.

```bash
curl "http://localhost:8000/api/v1/doctors/search?specialty=Vascular Surgery&institution=Cleveland Clinic&limit=20"
```

**Query Parameters:**
- `specialty`: Medical specialty filter
- `institution`: Institution name filter  
- `location`: Geographic location filter
- `skip`: Number of records to skip (pagination)
- `limit`: Maximum records to return (default: 20)

### Get Doctor Profile

**`GET /api/v1/doctors/{doctor_id}`**

Get detailed doctor information.

```bash
curl http://localhost:8000/api/v1/doctors/doc123
```

**Response:**
```json
{
  "doctor_id": "doc123",
  "full_name": "Dr. Sarah Johnson",
  "primary_specialty": "Vascular Surgery",
  "orcid": "0000-0002-1234-5678",
  "affiliations": [
    {
      "institution_name": "Cleveland Clinic",
      "role": "Attending Physician",
      "city": "Cleveland",
      "state": "OH"
    }
  ],
  "recent_publications": [
    {
      "title": "Outcomes in distal bypass surgery",
      "journal": "Journal of Vascular Surgery",
      "year": 2023,
      "doi": "10.1016/j.jvs.2023.01.001"
    }
  ]
}
```

## 📎 Upload API

### Get Presigned Upload URL

**`POST /api/v1/upload/presigned-url`**

Get a presigned URL for direct file upload to cloud storage.

```bash
curl -X POST http://localhost:8000/api/v1/upload/presigned-url \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "filename=medical-report.pdf" \
  -d "content_type=application/pdf"
```

**Response:**
```json
{
  "upload_url": "https://r2.cloudflarestorage.com/bucket/signed-url...",
  "key": "uploads/uuid/medical-report.pdf",
  "expires_in": 3600
}
```

## 🚨 Error Handling

All API endpoints return consistent error responses:

```json
{
  "error": "Validation error",
  "detail": "Invalid case JSON format",
  "status_code": 400,
  "timestamp": "2024-09-03T15:30:00Z"
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized  
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

### Common Error Types

**Validation Errors** (422):
```json
{
  "error": "Validation failed",
  "detail": [
    {
      "field": "case_json.condition.text",
      "message": "This field is required"
    }
  ]
}
```

**Not Found** (404):
```json
{
  "error": "Resource not found",
  "detail": "Case with ID 123 not found"
}
```

## 🔐 Authentication

### Bearer Token

Include JWT token in Authorization header:

```bash
curl -H "Authorization: Bearer your-jwt-token" \
  http://localhost:8000/api/v1/cases
```

### API Key (Workers)

For edge function calls, include API key:

```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8787/upload/presigned-url
```

## 📊 Rate Limiting

- **Rate Limit**: 100 requests per minute per IP
- **Burst**: Up to 20 requests in 10 seconds
- **Headers**: Rate limit info in response headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1693747800
```

## 🔗 Webhooks

### Stripe Payment Webhook

**`POST /api/v1/webhooks/stripe`**

Webhook endpoint for Stripe payment events.

**Headers Required:**
- `Stripe-Signature`: Webhook signature for verification

**Supported Events:**
- `checkout.session.completed`
- `payment_intent.succeeded`
- `payment_intent.payment_failed`

## 📱 SDK Examples

### TypeScript/JavaScript

```typescript
import { CaseJSONSchema } from '@another-doctor/ts-utils';

const api = new AnotherDoctorAPI('http://localhost:8000');

// Create case
const caseData = CaseJSONSchema.parse(rawCaseData);
const result = await api.createCase({
  raw_text: "Patient text...",
  casejson: caseData
});

// Find matches
const matches = await api.findMatches({
  case_json: caseData,
  filters: { min_year: 2019, max_results: 10 }
});
```

### Python

```python
from another_doctor_utils import HTTPClient, validate_case_json

async with HTTPClient("http://localhost:8000") as client:
    # Validate case data
    validate_case_json(case_data)
    
    # Create case
    response = await client.post("/api/v1/cases", json={
        "raw_text": "Patient text...",
        "casejson": case_data
    })
    
    case_id = response["case_id"]
```

## 📚 Schema Validation

All API requests/responses follow JSON schemas in [`packages/shared/schemas/`](../packages/shared/schemas/):

- **CaseJSON v1**: [`case-json-v1.json`](../packages/shared/schemas/case-json-v1.json)
- **Match Result v1**: [`match-result-v1.json`](../packages/shared/schemas/match-result-v1.json)

Use these schemas for client-side validation before making API calls.