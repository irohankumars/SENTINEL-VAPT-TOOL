# SENTINEL VAPT Tool

<p align="center">
  <strong>A simple dashboard for organizing authorized web security assessments.</strong>
</p>

<p align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=html,css,js,react,vite,python,fastapi,sqlite" alt="HTML, CSS, JavaScript, React, Vite, Python, FastAPI and SQLite" />
  </a>
</p>

SENTINEL brings projects, scans, findings, and reports into one place. It can run several security tools, normalize their results, remove duplicates, track finding status, and create reports that are easier to review and share.

> Use SENTINEL only on systems you own or have clear written permission to test.

## Purpose

Security tools often produce results in different formats. SENTINEL provides one workflow for starting an assessment and reviewing the outcome without switching between multiple terminals and report files.

It is useful for:

- Learning how a VAPT workflow is organized
- Running repeatable checks against authorized web targets
- Combining findings from different scanners
- Tracking findings by severity and status
- Exporting clear PDF and HTML reports

## Main features

- Dashboard with project, scan, and finding summaries
- Project management for web targets
- Built-in safe HTTP checks
- Support for httpx, Nuclei, and OWASP ZAP
- Normalized and deduplicated findings
- Severity, tool, status, and text filters
- Optional AI explanations for defensive guidance
- SQLite storage with no separate database server required
- PDF and HTML report generation
- Mock scanner mode for demos and local development

## Tech stack

| Area | Technology |
| --- | --- |
| Frontend | React, JavaScript, HTML, CSS |
| Build tool | Vite |
| Backend API | Python, FastAPI, Uvicorn |
| Database | SQLite, SQLAlchemy |
| Validation | Pydantic |
| Reports | ReportLab, Jinja2 |
| Security tools | Built-in HTTP scanner, httpx, Nuclei, OWASP ZAP |
| Optional AI | OpenAI-compatible API |

## Why use SENTINEL

- One view for results from multiple tools
- Less time spent sorting repeated findings
- Easy local setup for students and small teams
- Mock mode works without installing external scanners
- Reports are ready for technical review or project records
- Scanner paths are controlled by server configuration, not user input
- Private network targets are blocked by default for safer use

## How it works

```text
React dashboard
      |
FastAPI backend
      |
Scan orchestrator
      |
HTTP Scanner + httpx + Nuclei + OWASP ZAP
      |
Normalize + deduplicate + optional AI explanation
      |
SQLite database + PDF/HTML reports
```

## Requirements

- Node.js 20 or newer
- Python 3.12 or newer
- npm

External scanners are optional. The default mock mode lets you explore the complete interface without installing them.

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/irohankumars/SENTINEL-VAPT-TOOL.git
cd SENTINEL-VAPT-TOOL
```

### 2. Start the backend

Windows PowerShell:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python seed.py
uvicorn app.main:app --reload
```

macOS or Linux:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python seed.py
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive API documentation is available at `http://localhost:8000/docs`.

### 3. Start the frontend

Open another terminal in the project root:

```bash
npm install
```

Create the frontend environment file.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS or Linux:

```bash
cp .env.example .env
```

Then start the app:

```bash
npm run dev
```

Open `http://localhost:5173` in your browser.

## Using the app

1. Open **Projects** and create a project with an authorized HTTP or HTTPS target.
2. Start a new scan and select the tools you want to use.
3. Follow scan progress from the scan page.
4. Review and filter results from the **Findings** page.
5. Update a finding when it is confirmed, ignored, or resolved.
6. Download a PDF or HTML report after the scan completes.

## Scanner modes

### Mock mode

Mock mode is enabled by default in `backend/.env`:

```env
MOCK_SCANNERS=true
```

Use it to test the workflow safely without installing external security tools.

### Real scanner mode

Install [ProjectDiscovery httpx](https://github.com/projectdiscovery/httpx), [Nuclei](https://github.com/projectdiscovery/nuclei), and [OWASP ZAP](https://www.zaproxy.org/download/) from their official sources. Then update `backend/.env`:

```env
MOCK_SCANNERS=false
HTTPX_PATH=httpx
NUCLEI_PATH=nuclei
ZAP_URL=http://localhost:8080
```

Start the ZAP API before selecting OWASP ZAP for a scan. You can use any supported tool independently, so all three are not required at the same time.

## Optional AI explanations

The backend can request short defensive explanations from an OpenAI-compatible API. Add these values to `backend/.env`:

```env
AI_API_KEY=your_api_key
AI_API_URL=https://api.openai.com/v1
AI_MODEL=your_model_name
```

This feature is optional. Scanning, finding management, and reports still work without it.

## Useful commands

```bash
npm run dev       # Start the frontend development server
npm run build     # Create a production frontend build
npm run preview   # Preview the production build
```

Backend tests can be run from the `backend` directory:

```bash
pytest
```

## Important safety notes

- Never scan a target without permission.
- Active ZAP scans can generate heavy traffic and may change application state.
- Keep API keys in `backend/.env`. Do not commit that file.
- Leave `ALLOW_PRIVATE_TARGETS=false` unless you are working in an authorized local lab.
- Review scanner output before sharing a final report.

## Project structure

```text
SENTINEL/
|-- src/                  React frontend
|-- backend/app/          FastAPI application
|   |-- routers/          API routes
|   |-- scanners/         Scanner integrations
|   |-- services/         Scan and report logic
|   |-- models/           Database models
|   `-- reports/          PDF and HTML generation
|-- tools/                Project report utilities
|-- package.json          Frontend dependencies and commands
`-- README.md             Project guide
```

## License

No license has been added yet. Contact the repository owner before reusing or distributing the project.
