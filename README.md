# Zoho + Python Hybrid Backend (Django MVP)

Minimal API-first Django backend for a search/extract/score pipeline that can be triggered from Zoho Forms and later synced to Zoho Sheets.

## What this project does

- Receives sourcing requests over API.
- Runs a pipeline:
  - mock search
  - web content extraction
  - mock LLM-like scoring
  - placeholder Zoho Sheets sync
- Returns structured JSON results.
- Supports two sourcing scopes:
  - `candidates` for skilled trades talent
  - `projects` for U.S. data center construction project leads

## Tech stack

- Django + Django REST Framework
- Requests
- python-dotenv
- In-memory job storage for MVP

## Project structure

```text
.
├── api/
│   ├── auth.py
│   ├── serializers.py
│   ├── state.py
│   ├── urls.py
│   └── views.py
├── config/
│   ├── settings.py
│   └── urls.py
├── services/
│   ├── search_service.py
│   ├── extractor_service.py
│   ├── scoring_service.py
│   └── zoho_service.py
├── utils/
│   └── text_helpers.py
├── manage.py
└── requirements.txt
```

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` from `.env.example` and set your API key:

```env
SERVICE_API_KEY=your-strong-api-key
```

4. Run migrations:

```bash
python manage.py migrate
```

5. Start the server:

```bash
python manage.py runserver
```

## Authentication

All endpoints require:

```http
Authorization: Bearer <SERVICE_API_KEY>
```

`SERVICE_API_KEY` is validated by a simple Bearer token auth class (`api/auth.py`) to keep MVP setup lightweight.

## API endpoints

### `POST /api/start-job/`

Request:

```json
{
  "role": "HVAC Technician",
  "location": "Phoenix",
  "keywords": "HVAC, maintenance, service",
  "job_type": "onsite",
  "search_scope": "candidates"
}
```

Response:

```json
{
  "job_id": "UUID"
}
```

### `POST /api/run-job/`

Request:

```json
{
  "job_id": "UUID"
}
```

Response (sample):

```json
{
  "job_id": "UUID",
  "status": "completed",
  "errors": [],
  "results": [
    {
      "url": "https://example.com/...",
      "title": "HVAC opportunities in Phoenix",
      "snippet": "Search result snippet...",
      "match_role": true,
      "match_location": false,
      "score": 7,
      "reason": "contains role 'HVAC Technician'; matches 3 keyword(s)"
    }
  ],
  "zoho": {
    "status": "queued",
    "rows_prepared": 1,
    "message": "Payload ready for Zoho Sheets API integration."
  }
}
```

### `GET /api/job-status/<job_id>/`

Response:

```json
{
  "job_id": "UUID",
  "status": "completed",
  "progress": 100,
  "result_count": 2,
  "error_count": 0
}
```

## Postman collection (included)

Use the files in `postman/`:

- `Automated_Talent_API.postman_collection.json`
- `Automated_Talent_API.local.postman_environment.json`

Steps:

1. Import both files into Postman.
2. Select the `Automated Talent API - Local` environment.
3. Set `serviceApiKey` to the same value as `SERVICE_API_KEY` in `.env`.
4. Run `Start Job` then `Run Job` then `Job Status`.

The `Start Job` test script automatically saves `job_id` into `jobId` for the next requests.

## Zoho Forms payload examples

The Postman collection includes a folder named `Zoho Forms Payload Examples` with ready-to-run payloads:

- `Sample JSON webhook body` (illustrative Zoho-form-like submission body)
- `Mapped payload to Start Job schema` (exact shape this API expects)

For production Zoho webhook mapping, map your form fields to this backend payload shape:

```json
{
  "role": "HVAC Technician",
  "location": "Phoenix",
  "keywords": "HVAC, maintenance, service",
  "job_type": "onsite",
  "search_scope": "candidates"
}
```

For U.S. data center construction project sourcing, use:

```json
{
  "role": "Electrical Foreman",
  "location": "Texas",
  "keywords": "data center, construction, contractor, expansion",
  "job_type": "onsite",
  "search_scope": "projects"
}
```

## Notes for production hardening

- Replace in-memory `JOB_STORE` with persistent storage (DB/queue).
- Replace `run_search` mock with Tavily/Perplexity client.
- Replace `score_content` with actual LLM provider integration.
- Implement real Zoho OAuth + Sheets API writes in `zoho_service.py`.
- Add request throttling and structured logging.
