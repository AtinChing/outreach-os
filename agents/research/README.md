# Research Agent

The Research Agent is the first step in the lead generation pipeline. It discovers, enriches, and persists leads to Ghost DB.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RESEARCH AGENT                           │
│                                                             │
│  Input: job_id, connection_string                          │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   search.py  │───▶│  enrich.py   │───▶│  writer.py   │ │
│  │              │    │              │    │              │ │
│  │   HasData    │    │   OpenAI     │    │  Ghost DB    │ │
│  │  Maps search │    │   Analysis   │    │  (asyncpg)   │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│                                                             │
│  Output: RESEARCH_COMPLETE status + leads in Ghost DB      │
└─────────────────────────────────────────────────────────────┘
```

## Flow

1. **Search** (`search.py`): Calls the HasData Google Maps search API to find businesses
   - Text search with query (`q`)
   - Returns name, phone, address, website, rating in one response
   - Filters out permanently or temporarily closed businesses

2. **Enrich** (`enrich.py`): Uses OpenAI to analyze each lead
   - Scrapes website content
   - Generates 2-3 sentence research summary
   - Extracts email from website if available
   - Identifies business signals and pain points

3. **Write** (`writer.py`): Persists to Ghost DB
   - Inserts leads into job-specific DB
   - Updates master job status to `RESEARCH_COMPLETE`

## Environment Variables

Required in `.env`:

```bash
MASTER_DATABASE_URL=postgresql://ghost:***@<db>.ghost.build/postgres
HASDATA_API_KEY=...
OPENAI_API_KEY=sk-...
```

## Installation

```bash
cd agents/research
pip install -r requirements.txt
```

## Usage

### As a TrueFoundry Job

The Orchestrator will invoke this agent with:

```python
from agents.research import agent as research_agent

result = await research_agent.main(
    job_id="123e4567-e89b-12d3-a456-426614174000",
    connection_string="postgresql://ghost:***@job-db.ghost.build/postgres"
)
```

### CLI Testing

```bash
python agent.py \
  "123e4567-e89b-12d3-a456-426614174000" \
  "postgresql://ghost:***@job-db.ghost.build/postgres"
```

## Database Schema

### Master DB (`jobs` table)

```sql
CREATE TABLE jobs (
    job_id UUID PRIMARY KEY,
    query TEXT NOT NULL,
    status TEXT NOT NULL,  -- INITIATED → RESEARCH_COMPLETE
    db_connection_string TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Job DB (`leads` table)

```sql
CREATE TABLE leads (
    lead_id UUID PRIMARY KEY,
    job_id UUID NOT NULL,
    name TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    website TEXT,
    research_summary TEXT,
    status TEXT DEFAULT 'RESEARCHED',
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Error Handling

- If HasData API fails: raises `ValueError`
- If OpenAI API fails: raises exception, lead gets partial data
- If DB write fails: raises exception, job status set to `FAILED`
- All errors propagate to Orchestrator for retry logic

## Performance

- HasData search: typically batches results in one request (~1-3s for the search step)
- OpenAI enrichment: ~2-3s per lead
- Website scraping: ~1-2s per lead
- Total: ~4-6s per lead (dominated by enrichment and scraping)
- 10 leads: on the order of tens of seconds end-to-end (sequential enrichment)

## Cost Estimates

- HasData API: refer to current HasData pricing (order of ~$0.002 per lead for many queries)
- OpenAI API: ~$0.001 per lead (300 tokens output)
- Total: varies with HasData + OpenAI usage

## Testing

See `test_agent.py` for integration tests.

## Next Steps

After Research Agent completes:
1. Orchestrator triggers Strategy Agent
2. Strategy Agent reads leads from job DB
3. Strategy Agent generates call scripts + email templates
