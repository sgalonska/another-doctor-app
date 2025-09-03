# **A) Infrastructure & APIs**

## **A1. Core Architecture (LLM-minimal, PHI-safe)**

* **Frontend**

  * Next.js (React) on **Cloudflare Pages** (or Vercel)

  * Tailwind \+ shadcn/ui

  * Stripe Checkout for payments

* **Edge/API**

  * **Cloudflare Workers** for lightweight endpoints (presigned uploads, auth handoff)

  * **Webhooks** (Stripe) → enqueue jobs

* **Backend (App & ETL)**

  * **FastAPI** (Python) for patient/admin APIs

  * **RQ/Celery** workers for extraction, ingestion, scoring

* **Storage & Databases**

  * **Cloudflare R2** (S3-compatible) for uploads (encrypted at rest)

  * **Postgres** (Supabase/Render) → canonical structured data

  * **Qdrant** (cloud/self-host) → vector search (HNSW, payload filters)

  * (Optional) **OpenSearch** (BM25) for keyword \+ filters

* **Analytics & Logs**

  * Structured logs (JSON) \+ audit trails for PHI access

  * Basic observability: Grafana/Prometheus or hosted alternative

### **Security/Compliance Defaults**

* PHI **never** leaves your infra

* De-identify **before** any LLM call

* Row-level access control; short-lived signed URLs for files

* Audit logging of PHI access

* Data retention defaults, delete on request

---

## **A2. Internal Services**

* **Patient Intake**: upload/paste → presigned R2 upload → job enqueue

* **Parsing Service** (no LLM): OCR (if needed) → scispaCy/MedCAT → UMLS/SNOMED/ICD mapping → **CaseJSON**

* **De-Identification**: Safe Harbor removal; generate **Synthetic Abstract**

* **Doctor KB Ingestion** (ETL): PubMed/OpenAlex/CT.gov/NIH RePORTER/Crossref → Postgres \+ Qdrant

* **Matching Engine**: hybrid retrieval (filters \+ vectors) → aggregate to doctors → score → shortlist

* **Navigator Console**: review/approve matches; generate specialist cards; send intros

* **Patient Portal**: Upload → Parsed Diagnosis preview (human \+ machine) → Checkout → Timeline

---

## **A3. Open APIs (all free to start)**

1. **PubMed / Entrez**

   * What: biomedical publications (authors, affiliations, MeSH)

   * Use: topic pubs → authors (doctors) \+ institutions

Example:

 `esearch:  .../esearch.fcgi?db=pubmed&retmode=json&retmax=50&term="critical limb ischemia"[MeSH Terms] AND (distal bypass OR pedal loop)`  
`efetch:   .../efetch.fcgi?db=pubmed&retmode=xml&id=PMID1,PMID2`

*   
2. **OpenAlex**

   * What: works, authors (IDs/ORCID), institutions, concepts, citations

   * Use: author ↔ institution graph, clean JSON

Example:

 `https://api.openalex.org/works?search=critical limb ischemia distal bypass&per_page=25&sort=publication_year:desc`

*   
3. **ClinicalTrials.gov**

   * What: trials, **PI names**, sponsors, sites

   * Use: PI \= strong expertise signal; site \= institutional strength

Example:

 `https://clinicaltrials.gov/api/query/full_studies?expr=critical limb ischemia AND (bypass OR revascularization)&min_rnk=1&max_rnk=50&fmt=json`

*   
4. **ORCID (Public)**

   * What: researcher IDs, claimed works, affiliations (disambiguation)

Example:

 `search: https://pub.orcid.org/v3.0/search/?q=family-name:Smith AND given-names:John`  
`record: https://pub.orcid.org/v3.0/0000-0002-XXXX-YYYY`

*   
5. **NIH RePORTER**

   * What: US grants (PI, institution, year, abstracts)

   * Use: funding signal → doctor & institution scores

Example:

 `POST https://api.reporter.nih.gov/v2/projects/search`  
`{"criteria":{"text_phrase":"critical limb ischemia OR limb salvage"}, "include_fields":[...], "limit":25}`

*   
6. **Crossref**

   * What: DOIs & metadata (title, year, authors, journal)

   * Use: DOI normalization; backfill metadata

Example (include User-Agent mailto):

 `https://api.crossref.org/works?query=critical limb ischemia distal bypass&rows=25&sort=issued&order=desc`

*   
7. **EUCTR** (web)

   * What: EU trials (less uniform JSON)

   * Use: complement CT.gov; scrape politely/cache

Example:

 `https://www.clinicaltrialsregister.eu/ctr-search/search?query=critical+limb+ischemia`

*   
8. **Specialty Societies** (web)

   * What: leadership, awards, committees

   * Use: bonus peer-recognition signals (manual/light scraping)

---

## **A4. Data Model (Postgres, minimal)**

`-- Canonical entities`  
`CREATE TABLE institution (`  
  `institution_id UUID PRIMARY KEY,`  
  `source TEXT[], name TEXT NOT NULL,`  
  `city TEXT, state TEXT, country TEXT,`  
  `created_at TIMESTAMPTZ DEFAULT now()`  
`);`

`CREATE TABLE doctor (`  
  `doctor_id UUID PRIMARY KEY,`  
  `full_name TEXT NOT NULL,`  
  `orcid TEXT, npi TEXT, primary_specialty TEXT,`  
  `created_at TIMESTAMPTZ DEFAULT now()`  
`);`

`CREATE TABLE doctor_affiliation (`  
  `doctor_id UUID REFERENCES doctor(doctor_id),`  
  `institution_id UUID REFERENCES institution(institution_id),`  
  `role TEXT, start_year INT, end_year INT,`  
  `PRIMARY KEY (doctor_id, institution_id, role, start_year)`  
`);`

`CREATE TABLE work (`  
  `work_id UUID PRIMARY KEY,`  
  `source TEXT NOT NULL,          -- 'pubmed'|'openalex'|'crossref'|'ctgov'|'nih_reporter'|'euctr'`  
  `source_key TEXT NOT NULL,      -- PMID | DOI | OpenAlex ID | NCT ID | ProjectNum ...`  
  `title TEXT, abstract TEXT, year INT, doi TEXT,`  
  `mesh_terms TEXT[], url TEXT, raw JSONB,`  
  `created_at TIMESTAMPTZ DEFAULT now(),`  
  `UNIQUE (source, source_key)`  
`);`

`CREATE TABLE doctor_work (`  
  `doctor_id UUID REFERENCES doctor(doctor_id),`  
  `work_id UUID REFERENCES work(work_id),`  
  `author_position INT, is_pi BOOLEAN,`  
  `PRIMARY KEY (doctor_id, work_id)`  
`);`

`CREATE TABLE topic (`  
  `topic_id UUID PRIMARY KEY,`  
  `name TEXT UNIQUE NOT NULL,`  
  `synonyms TEXT[]`  
`);`

`CREATE TABLE doctor_topic_score (`  
  `doctor_id UUID REFERENCES doctor(doctor_id),`  
  `topic_id UUID REFERENCES topic(topic_id),`  
  `components JSONB,              -- {pubs_5y:3, trials_pi:1, grants:2, inst_pubs:25,...}`  
  `score NUMERIC, updated_at TIMESTAMPTZ DEFAULT now(),`  
  `PRIMARY KEY (doctor_id, topic_id)`  
`);`

`-- Patient case specs / term cache`  
`CREATE TABLE case_spec (`  
  `case_id UUID PRIMARY KEY,`  
  `casejson JSONB NOT NULL,       -- de-identified machine-readable case`  
  `created_at TIMESTAMPTZ DEFAULT now(),`  
  `version TEXT DEFAULT 'v1'`  
`);`

`CREATE TABLE term_cache (`  
  `lemma TEXT PRIMARY KEY,`  
  `mesh TEXT[], snomed TEXT[], icd10 TEXT[],`  
  `canonical_label TEXT,`  
  `updated_at TIMESTAMPTZ DEFAULT now()`  
`);`

**Vectors (Qdrant)**

* `works_vectors` — embeddings of `title+abstract` (PubMed/OpenAlex/CT.gov/NIH)

  * Payload: `{source,source_key,year,mesh_terms[],author_ids[],institution_ids[],country,is_pi}`

* (Optional) `doctor_topic_vectors` — pooled vectors per doctor/topic

* `case_vectors` — embeddings of **Synthetic Abstract** (de-ID)

---

## **A5. Matching & Scoring (transparent)**

* **Hybrid retrieval**

  1. Symbolic filter (year ≥ 2019, MeSH includes PAD/Ischemia, specialty, geo)

  2. Vector search (Qdrant, cosine) using **Synthetic Abstract**

  3. Aggregate hits → per-doctor

**Scoring**

 `doctor_score = 2*pubs_5y + 5*trials_pi + 1*citations_bucket`  
`inst_score   = 0.5*inst_pubs + 2*inst_trials + 0.5*nih_grants`  
`total        = doctor_score + 0.5*inst_score`

*   
* **Explainability**: attach evidence (PMIDs, NCT IDs, grant IDs, titles, years)

---

# **B) Data Flow (with concrete examples)**

## **B1. Intake → Dual Outputs (Human \+ Machine)**

**Input (user upload/paste):**

“Severe artery disease in the left foot; prior anterior tibial angioplasty failed; surgeon recommends transmetatarsal amputation; patient wants to avoid amputation.”

**Extraction (no LLM):**

* OCR (if needed) → text

* scispaCy/MedCAT \+ dictionaries → entities \+ codes

* Rules: detect laterality, prior intervention status, goal

**Human-Readable Brief (templated, editable by user):**

“We read your report as showing **critical limb ischemia** in your **left foot**.  
 A previous **angioplasty** did not succeed.  
 Your goal is to **avoid amputation** and consider **limb-salvage options**.”

**Machine-Readable CaseJSON (de-ID):**

`{`  
  `"condition": {"text":"critical limb ischemia","icd10":"I70.25","snomed":"443165006","mesh":"D016491"},`  
  `"anatomy": {"site":"foot","laterality":"left","arterial_segments":["anterior tibial"]},`  
  `"prior_interventions": [{"name":"angioplasty","target":"anterior tibial","status":"failed"}],`  
  `"comorbidities": ["type 2 diabetes"],`  
  `"goals": ["avoid amputation","limb salvage"],`  
  `"urgency": "high",`  
  `"keywords": ["distal bypass","pedal loop","tibial arch"],`  
  `"date_anchor": "2025-08"`  
`}`

**Synthetic Abstract (for embeddings; still de-ID; templated):**  
 “Adult with peripheral arterial disease presenting as **critical limb ischemia** of the **left foot**. Prior **angioplasty** of the **anterior tibial artery** was **unsuccessful**. Goal: **limb salvage** and avoidance of amputation; consider **distal bypass** or **pedal loop revascularization**.”

---

## **B2. Query Pack generated from CaseJSON**

**PubMed (MeSH \+ keywords):**

`("Ischemia"[MeSH] OR "Peripheral Arterial Disease"[MeSH] OR "Critical Limb Ischemia")`  
`AND ("Bypass, Surgical"[MeSH] OR "distal bypass" OR "pedal loop" OR "tibial arch")`  
`AND ("Foot"[MeSH] OR foot OR "anterior tibial")`  
`AND ("2019/01/01"[Date - Publication] : "3000"[Date - Publication])`

**OpenAlex:**

`search=critical limb ischemia distal bypass "anterior tibial" pedal loop`  
`&per_page=50&sort=publication_year:desc`

**ClinicalTrials.gov:**

`critical limb ischemia AND (distal bypass OR revascularization OR pedal loop)`

**Qdrant Vector Search:**

* Query vector \= embedding(Synthetic Abstract)

* Filter payload: `year >= 2019`, `mesh_terms intersects {Ischemia, Peripheral Arterial Disease}`, optional geo

---

## **B3. Aggregation → Scoring → Shortlist**

1. Collect hits (works, trials) per **doctor\_id**

2. Calculate components:

   * `pubs_5y` \= count of topic-relevant pubs since 2019

   * `trials_pi` \= trials where doctor is PI

   * `inst_pubs`, `inst_trials`, `nih_grants` via affiliations

3. Score with formula above

4. Produce candidate list with **evidence**:

`[`  
  `{`  
    `"doctor_id": "uuid-123",`  
    `"name": "Dr. A",`  
    `"institution": "Cleveland Clinic",`  
    `"score": 27.0,`  
    `"components": {"pubs_5y":3,"trials_pi":1,"inst_pubs":25,"inst_trials":3},`  
    `"evidence": [`  
      `{"type":"pubmed","pmid":"12345678","title":"Distal bypass in CLI","year":2023},`  
      `{"type":"ctgov","nct":"NCT01234567","role":"PI","title":"Pedal loop trial"},`  
      `{"type":"nih_reporter","project":"R01-XXXX","fiscal_year":2024}`  
    `]`  
  `},`  
  `{ "... next doctor ..." }`  
`]`

---

## **B4. Human Review & Delivery**

* **Navigator Console** shows top 10 with components/evidence

* Approve **2–3 specialists**

* Generate **Specialist Cards** (patient-facing) from data (no LLM required)

* **Warm Intro Emails** (templated) to specialists (no medical advice, attach Case Brief)

*(Optional) If you want polished prose: send **only de-ID facts** to ChatGPT to produce short justifications. No browsing; strict schema.)*

---

## **B5. Refund/Timers/SLAs**

* Stripe webhook → case “active”

* Timer (30 days) → auto-refund if `< 2` intros delivered

* SLA metric: time to 1st/2nd intro; navigator reminders at Day 5/14

---

# **C) Machine-Readable Build Spec (drop-in for an LLM)**

`{`  
  `"project": "another.doctor",`  
  `"goal": "Parse patient reports, create a human-readable brief and machine-readable CaseJSON, match to specialists from public data with transparent scoring.",`  
  `"stack": {`  
    `"frontend": "Next.js + Tailwind + shadcn/ui on Cloudflare Pages",`  
    `"edge_api": "Cloudflare Workers (presigned uploads, auth handshake)",`  
    `"backend": "FastAPI (Python) + RQ/Celery workers",`  
    `"storage": "Cloudflare R2 (S3 compatible) for uploads",`  
    `"db": "Postgres (canonical), Qdrant (vectors), OpenSearch (optional BM25)",`  
    `"payments": "Stripe Checkout + webhooks",`  
    `"nlp": "scispaCy/MedCAT + UMLS/SNOMED/ICD linking (no LLM for PHI)",`  
    `"embeddings": "PubMed-tuned sentence transformers for literature; Synthetic Abstract for cases",`  
    `"llm_usage": "Optional, de-identified only, for final phrasing/re-ranking explanations"`  
  `},`  
  `"apis": [`  
    `{"name":"PubMed/Entrez","purpose":"publications","key_endpoints":["esearch","efetch"]},`  
    `{"name":"OpenAlex","purpose":"works/authors/institutions","key_endpoints":["/works"]},`  
    `{"name":"ClinicalTrials.gov","purpose":"trials + PIs","key_endpoints":["/query/full_studies"]},`  
    `{"name":"ORCID","purpose":"author disambiguation","key_endpoints":["/search","/{orcid}"]},`  
    `{"name":"NIH RePORTER","purpose":"grants","key_endpoints":["/v2/projects/search"]},`  
    `{"name":"Crossref","purpose":"DOI metadata","key_endpoints":["/works"]},`  
    `{"name":"EUCTR","purpose":"EU trials","access":"polite scraping"},`  
    `{"name":"Societies","purpose":"leadership/awards","access":"manual/light scraping"}`  
  `],`  
  `"casejson_schema_v1": {`  
    `"condition": {"text":"string","icd10":"string","snomed":"string","mesh":"string"},`  
    `"anatomy": {"site":"string","laterality":"string","arterial_segments":["string"]},`  
    `"prior_interventions": [{"name":"string","target":"string","status":"string","date_approx":"string"}],`  
    `"comorbidities": ["string"],`  
    `"goals": ["string"],`  
    `"urgency": "string",`  
    `"keywords": ["string"],`  
    `"date_anchor": "string"`  
  `},`  
  `"synthetic_abstract_template": "Adult with peripheral arterial disease presenting as {condition} of the {laterality} {site}. Prior {intervention} on {target} was {status}. Goal: {goals}.",`  
  `"retrieval": {`  
    `"symbolic_filters": ["year>=2019","mesh_terms includes PAD/Ischemia","specialty","geo"],`  
    `"vector_search": "Qdrant cosine over works_vectors using Synthetic Abstract embedding",`  
    `"aggregate_to_doctor": true`  
  `},`  
  `"scoring": {`  
    `"doctor_score": "2*pubs_5y + 5*trials_pi + 1*citations_bucket",`  
    `"institution_score": "0.5*inst_pubs + 2*inst_trials + 0.5*nih_grants",`  
    `"total": "doctor_score + 0.5*institution_score",`  
    `"explain": "attach PMIDs, NCT IDs, grant IDs, titles/years"`  
  `},`  
  `"workflow": [`  
    `"Upload → R2",`  
    `"OCR (if needed) → Text",`  
    `"Deterministic NER/linking → CaseJSON",`  
    `"Generate Human Brief (template) + show for edit",`  
    `"De-identify + Synthetic Abstract",`  
    `"Query Pack (PubMed/OpenAlex/CT.gov + vector search)",`  
    `"Aggregate + Score + Evidence",`  
    `"Navigator approves 2–3 matches",`  
    `"Generate Specialist Cards + Send intros",`  
    `"SLA timers + refund logic"`  
  `],`  
  `"compliance": {`  
    `"phi_in_llm": false,`  
    `"deid_rules": ["names","geo<state","dates→month/year","contacts","IDs","device IDs","photos"],`  
    `"logging": "audit PHI access; separate de-ID prompt logs",`  
    `"retention": "defaults + delete on request"`  
  `}`  
`}`

---

# **Recommended repo strategy: Monorepo**

## **Why monorepo (for your case)**

* **One source of truth** for contracts (e.g., CaseJSON schema) shared by frontend \+ backend \+ workers.

* **Atomic changes** across UI/API/ETL (no cross-repo PR dance).

* **Shared tooling** (linting, CI, infra templates).

* Easy to split later if needed.

---

# **Directory blueprint**

`another-doctor/`  
`├─ apps/`  
`│  ├─ frontend/                 # Next.js app (Cloudflare Pages or Vercel)`  
`│  │  ├─ src/`  
`│  │  ├─ public/`  
`│  │  ├─ package.json`  
`│  │  └─ ...`   
`│  ├─ backend/                  # FastAPI (patient/admin APIs)`  
`│  │  ├─ src/`  
`│  │  │  ├─ anotherdoctor/`  
`│  │  │  │  ├─ api/             # route handlers`  
`│  │  │  │  ├─ core/            # settings, logging, security`  
`│  │  │  │  ├─ services/        # case parser, matching adapters`  
`│  │  │  │  ├─ schemas/         # Pydantic models (CaseJSON, etc.)`  
`│  │  │  │  └─ db/              # SQLAlchemy, migrations`  
`│  │  ├─ pyproject.toml`  
`│  │  └─ ...`  
`│  ├─ workers/                  # RQ/Celery/Dagster jobs (OCR, ETL, scoring)`  
`│  │  ├─ ingestion/             # PubMed/OpenAlex/CT.gov jobs`  
`│  │  ├─ parsing/               # OCR + deterministic extraction`  
`│  │  ├─ scoring/               # weekly recompute`  
`│  │  └─ pyproject.toml`  
`│`  
`├─ packages/`  
`│  ├─ shared/                   # cross-lang contracts (JSON Schemas, OpenAPI)`  
`│  │  ├─ schemas/               # CaseJSON schema, output card schema`  
`│  │  ├─ queries/               # canned PubMed/OpenAlex queries`  
`│  │  └─ README.md`  
`│  ├─ ts-utils/                 # shared TypeScript utils/types`  
`│  └─ py-utils/                 # shared Python utilities (retry, http client)`  
`│`  
`├─ infra/`  
`│  ├─ docker/                   # Dockerfiles for backend/workers`  
`│  ├─ terraform/                # R2 bucket, Postgres, Qdrant, secrets`  
`│  ├─ k8s/                      # (optional) manifests if you move to K8s`  
`│  └─ cloudflare/               # Workers scripts, routes, wrangler.toml`  
`│`  
`├─ .github/`  
`│  ├─ workflows/                # CI/CD pipelines`  
`│  └─ ISSUE_TEMPLATE/`  
`│`  
`├─ Makefile                     # dx shortcuts: make dev, make test, make seed`  
`├─ turbo.json / pnpm-workspace.yaml (if using JS workspaces)`  
`├─ README.md`  
`└─ LICENSE`

---

# **Tooling choices (pragmatic)**

* **JS/TS:** pnpm workspaces \+ Turborepo for `apps/frontend` and `packages/ts-utils`.

* **Python:** Poetry (or uv) for `apps/backend` and `apps/workers`; Ruff \+ Black for lint/format.

* **API contracts:** Pydantic models in backend generate **OpenAPI**; mirror the JSON Schemas in `packages/shared/schemas` so frontend can validate forms without drift.

* **Infra:** Terraform modules for Postgres/Qdrant/R2/Secrets. Keep `wrangler.toml` (Cloudflare Workers) in `infra/cloudflare/`.

* **Containers:** One image for `backend`, one for `workers`. `frontend` deploys via Pages/Vercel without a container.

---

# **CI/CD (minimal but solid)**

* **Checks on PR:**

  * Frontend: `pnpm i && pnpm lint && pnpm build`

  * Backend/Workers: `poetry install && ruff check && pytest`

  * Generate OpenAPI & validate JSON Schemas (fail if drift).

* **Deploy on main:**

  * Frontend → Cloudflare Pages (or Vercel)

  * Backend/Workers → Render/Fly.io (or your container registry \+ deploy)

  * Run DB migrations automatically (e.g., Alembic)

---

# **Environments & secrets**

* `.env.example` at repo root; **never commit real secrets**.

* Use **Cloudflare Secrets** for Worker env; **Terraform** to wire secrets to backend/workers (or 1Password/GCP Secret Manager).

* Keep **per-env config** (dev/stage/prod) in `infra/terraform/` workspaces.

---

# **Testing strategy**

* **Unit**: extraction rules (deterministic), API route handlers, scoring math.

* **Contract**: schema validation—frontend uses the same CaseJSON schema as backend.

* **Integration**: ETL jobs hit sandbox APIs (record with VCR.py); DB seed fixtures for topic “CLI”.

* **Golden tests**: sample input → expected CaseJSON → expected top-5 doctors (by stable seed DB).

---

# **When to split repos later**

Move to polyrepo when:

* Teams are independent and releases decouple (e.g., infra as code, separate ETL cadence).

* Compliance dictates separate audit trails (rare for an MVP).

* Build times or CI complexity become a drag.

If you do split:

* Keep `packages/shared` (schemas/contracts) in its own repo and pin versions from frontend/backend.

---

# **Quick start commands (example)**

**Root Makefile**

`dev: ## start all dev services`  
`\tpnpm -C apps/frontend dev &`  
`\tpoetry -C apps/backend run uvicorn anotherdoctor.api:app --reload &`  
`\tpoetry -C apps/workers run rq worker --with-scheduler`

`test:`  
`\tpnpm -C apps/frontend test`  
`\tpoetry -C apps/backend run pytest`  
`\tpoetry -C apps/workers run pytest`

`build:`  
`\tpnpm -C apps/frontend build`  
`\tpoetry -C apps/backend build`  
