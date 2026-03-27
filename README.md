# Research to Outreach

Research to Outreach is a monorepo that automates lead research and outreach by combining an AI research agent (powered by Anthropic) with a FastAPI backend and a React frontend. Given a search query, the system finds leads, enriches them with contact details and a research summary, and surfaces them in a dashboard for review and outreach.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LAYER                              │
│  Slack Bot → Orchestrator → Research Agent → Strategy Agent    │
│  → Outreach Agent → Follow-up Agent                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER (Ghost DB)                      │
│  Master DB: jobs table                                          │
│  Per-Job DB: leads, strategy, email_log tables                 │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### Research Agent ✅ IMPLEMENTED
- **Location**: `agents/research/`
- **Purpose**: Discovers and enriches leads using HasData + Gemini Flash
- **Speed**: ~2 seconds per lead (ultra-fast!)
- **Cost**: $0.002 per lead (200 leads FREE!)
- **Input**: job_id, query (e.g., "plumbing in Austin TX"), job_connection_string
- **Output**: Enriched leads in Ghost DB, job status → RESEARCH_COMPLETE
- **Docs**: See `agents/research/README.md` and `agents/research/QUICKSTART.md`

### Backend (FastAPI)
- **Location**: `backend/`
- **Purpose**: REST API for frontend, orchestrates agent pipeline
- **Stack**: FastAPI, asyncpg, Auth0

### Frontend (React)
- **Location**: `frontend/`
- **Purpose**: Dashboard for viewing jobs and leads
- **Stack**: React, TypeScript, Vite

### Database (Ghost/PostgreSQL)
- **Location**: `db/`
- **Schema**: `master_schema.sql` (jobs), `job_schema.sql` (leads)

## Getting Started

### Quick Start (Research Agent Only)

1. Install dependencies:
```bash
cd agents/research
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run test:
```bash
cd agents/research
python test_agent.py
```

See `agents/research/QUICKSTART.md` for detailed setup.

### Full Stack

1. Clone the repository: 
```bash
git clone <repo-url> && cd research-to-outreach
```

2. Copy the example env file: 
```bash
cp .env.example .env
# Fill in your credentials
```

3. Start all services: 
```bash
docker-compose up
```

## Environment Variables

Required in `.env`:

```bash
# Master Ghost DB
MASTER_DATABASE_URL=postgresql://ghost:***@<db>.ghost.build/postgres

# API Keys (both FREE tier available!)
HASDATA_API_KEY=your-api-key-here  # 200 leads FREE
GEMINI_API_KEY=AIzaSy...           # FREE tier
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_AUDIENCE=your-api-identifier
```

## Project Structure

```
.
├── agents/
│   └── research/          # Research Agent (COMPLETE)
│       ├── agent.py       # Main orchestration
│       ├── search.py      # Google Maps API integration
│       ├── enrich.py      # Claude enrichment
│       ├── writer.py      # Ghost DB persistence
│       ├── test_agent.py  # Integration tests
│       └── README.md      # Full documentation
├── backend/
│   ├── main.py           # FastAPI app
│   ├── orchestrator.py   # Pipeline orchestration
│   └── auth.py           # Auth0 integration
├── frontend/
│   └── src/              # React app
├── db/
│   ├── master_schema.sql # Jobs table
│   ├── job_schema.sql    # Leads table
│   └── models.py         # Pydantic models
└── deploy/
    ├── Dockerfile.research
    └── truefoundry.yaml
```

## Development Status

- ✅ Research Agent: Complete and tested
- 🚧 Strategy Agent: TODO
- 🚧 Outreach Agent: TODO
- 🚧 Follow-up Agent: TODO
- 🚧 Orchestrator: Partial
- 🚧 Frontend: Partial

## Documentation

- Research Agent: `agents/research/README.md`
- Quick Start: `agents/research/QUICKSTART.md`
- Integration: `agents/research/INTEGRATION.md`

## Testing

```bash
# Test Research Agent
cd agents/research
python test_agent.py

# Expected: 5 leads found, enriched, and saved to Ghost DB
```

## Deployment

See `agents/research/INTEGRATION.md` for TrueFoundry deployment instructions.

## License

MIT
