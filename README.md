# AI Agent Workflow

LangGraph agent with tool calling and a Redis job queue for async runs.

## Setup

```bash
cp .env.example .env
docker compose up -d
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run API and worker in separate terminals:

```bash
uvicorn app.main:app --reload --port 8001
python -m app.worker
```

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/jobs` | Queue a workflow job |
| GET | `/jobs/{job_id}` | Fetch job status/result |
| POST | `/run` | Execute synchronously (dev) |

### Queue a job

```bash
curl -X POST http://localhost:8001/jobs \
  -H "Content-Type: application/json" \
  -d '{"task": "Summarize open invoices for ACME and flag anything over 5000"}'
```

## Tools

Built-in tools:

- `lookup_account` — fetch account metadata
- `list_invoices` — list invoices for an account
- `calculate_total` — sum numeric values

Data is mocked in `app/tools.py` for local demos.
