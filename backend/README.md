# SentinelVAPT backend

SentinelVAPT is an educational web-security assessment orchestrator. The FastAPI backend creates projects and scans, runs configured httpx/Nuclei/ZAP adapters, normalizes and deduplicates findings, optionally explains them through an OpenAI-compatible API, stores data in SQLite, and exports PDF or HTML reports.

> Only scan targets you own or have explicit written permission to assess. Active ZAP scans can generate significant traffic and modify application state.

## Architecture

`React → FastAPI → scan orchestrator → httpx / Nuclei / ZAP → normalize → deduplicate → optional AI explanation → SQLite → reports`

## Requirements

- Python 3.12 or newer
- Node.js 20 or newer
- External scanners are optional when `MOCK_SCANNERS=true`

## Backend setup (Windows PowerShell)

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python seed.py
uvicorn app.main:app --reload
```

macOS/Linux activation is `source .venv/bin/activate`. The API runs at `http://localhost:8000`; Swagger is available at `/docs` and ReDoc at `/redoc`.

## Frontend setup

From the repository root:

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

The frontend uses `VITE_API_URL=http://localhost:8000/api` by default.

## Environment variables

- `DATABASE_URL`: SQLAlchemy database URL
- `HTTPX_PATH`, `NUCLEI_PATH`: trusted server-configured executable paths
- `ZAP_URL`: local ZAP API base URL
- `SCANNER_TIMEOUT`: per-tool timeout in seconds
- `ALLOW_PRIVATE_TARGETS`: permit private/loopback targets in controlled labs; defaults to `false`
- `MAX_RESPONSE_BYTES`: maximum response body read by the built-in HTTP scanner
- `MOCK_SCANNERS`: use safe local sample results
- `AI_API_KEY`, `AI_API_URL`, `AI_MODEL`: optional explanation provider
- `CORS_ORIGINS`: comma-separated development origins

The backend works without AI configuration. In that case `ai_explanation` remains null.

## Scanner installation

Install ProjectDiscovery [httpx](https://github.com/projectdiscovery/httpx) and [Nuclei](https://github.com/projectdiscovery/nuclei) using their official release instructions, then set their executable paths in `.env`. Install [OWASP ZAP](https://www.zaproxy.org/download/) and start its local API on the configured `ZAP_URL`.

No executable path or command is accepted through the API. Targets are restricted to HTTP and HTTPS URLs, processes use argument arrays without a shell, and scans have configured timeouts.

The built-in HTTP scanner performs safe GET-only checks for browser security headers, server disclosure, redirects, HTTPS/HSTS observations, and cookie attributes. It enforces connection limits, redirect limits, timeouts, response-size limits, and public-network-only resolution by default. Set `ALLOW_PRIVATE_TARGETS=true` only for an authorized local lab.

## Mock scanner mode

Keep this setting for development and demonstrations without external tools:

```env
MOCK_SCANNERS=true
```

Create a scan with `POST /api/scans`, then start it with `POST /api/scans/{id}/start`. The frontend polls `GET /api/scans/{id}` until it completes.

## API overview

- Projects: `GET/POST /api/projects`, `GET/PUT/DELETE /api/projects/{id}`
- Scans: `GET/POST /api/scans`, `GET /api/scans/{id}`, `POST /start`, `POST /cancel`
- Findings: `GET /api/findings`, `GET /api/findings/{id}`, `PATCH /status`
- Reports: `GET /api/reports/{scan_id}/pdf` and `/html`
- Health: `GET /api/health`

Finding filters include `severity`, `tool`, `status`, `search`, `project_id`, and `scan_id`.
