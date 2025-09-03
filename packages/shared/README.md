# Shared Packages

This directory contains shared contracts and utilities used across the Another Doctor monorepo.

## Directory Structure

```
packages/
├── shared/           # Cross-language contracts
│   ├── schemas/      # JSON Schemas for data validation
│   └── queries/      # Canned query templates for external APIs
├── ts-utils/         # Shared TypeScript utilities
└── py-utils/         # Shared Python utilities
```

## JSON Schemas

### CaseJSON v1 (`schemas/case-json-v1.json`)

The canonical schema for machine-readable medical case representation. Used by:
- Backend for validation during case parsing
- Frontend for form validation
- Workers for ETL pipeline validation

### Match Result v1 (`schemas/match-result-v1.json`)

Schema for specialist match results. Ensures consistency between:
- Backend matching service output
- Frontend specialist card display
- Navigator console review interface

## Query Templates

### PubMed Templates (`queries/pubmed-templates.json`)

Pre-built query templates for common medical conditions using MeSH terms and keywords.

### OpenAlex Templates (`queries/openalex-templates.json`)

Query templates for academic works and author searches.

## Usage

### Backend (Python)
```python
import json
from jsonschema import validate

# Load and validate CaseJSON
with open("packages/shared/schemas/case-json-v1.json") as f:
    schema = json.load(f)

validate(instance=case_data, schema=schema)
```

### Frontend (TypeScript)
```typescript
import caseJsonSchema from "../../packages/shared/schemas/case-json-v1.json";
import Ajv from "ajv";

const ajv = new Ajv();
const validateCaseJson = ajv.compile(caseJsonSchema);

if (!validateCaseJson(caseData)) {
  console.error("Invalid CaseJSON:", validateCaseJson.errors);
}
```

## Versioning

Schemas are versioned (e.g., `case-json-v1.json`) to support backward compatibility during API evolution. When making breaking changes:

1. Create new version file (e.g., `case-json-v2.json`)
2. Update backend to support both versions
3. Migrate frontend to new version
4. Deprecate old version after migration period

## Validation

All schemas are validated in CI/CD pipelines to ensure:
- Valid JSON Schema syntax
- No drift between backend Pydantic models and JSON schemas
- Frontend type definitions match schema contracts