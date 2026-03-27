# Research Agent Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      RESEARCH AGENT                             │
│                                                                 │
│  Input: job_id, query, job_connection_string, lead_count       │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    SEARCH PHASE                          │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────┐     │  │
│  │  │  Google Maps Places API                        │     │  │
│  │  │  - Text Search: "plumbing in Austin TX"        │     │  │
│  │  │  - Returns: place_id, name, rating             │     │  │
│  │  └────────────────────────────────────────────────┘     │  │
│  │                        ↓                                 │  │
│  │  ┌────────────────────────────────────────────────┐     │  │
│  │  │  Google Maps Place Details API                 │     │  │
│  │  │  - Input: place_id                             │     │  │
│  │  │  - Returns: phone, address, website            │     │  │
│  │  └────────────────────────────────────────────────┘     │  │
│  │                        ↓                                 │  │
│  │  Result: List[{name, phone, address, website, rating}]  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   ENRICH PHASE                           │  │
│  │                                                          │  │
│  │  For each lead:                                          │  │
│  │  ┌────────────────────────────────────────────────┐     │  │
│  │  │  Website Scraper (BeautifulSoup)              │     │  │
│  │  │  - Fetch website HTML                          │     │  │
│  │  │  - Extract clean text (remove nav, footer)     │     │  │
│  │  │  - Limit to 8k chars                           │     │  │
│  │  └────────────────────────────────────────────────┘     │  │
│  │                        ↓                                 │  │
│  │  ┌────────────────────────────────────────────────┐     │  │
│  │  │  Claude API (Anthropic)                        │     │  │
│  │  │  - Model: claude-3-5-sonnet-20241022           │     │  │
│  │  │  - Input: business info + website text         │     │  │
│  │  │  - Output: 2-3 sentence summary                │     │  │
│  │  │  - Focus: services, signals, pain points       │     │  │
│  │  └────────────────────────────────────────────────┘     │  │
│  │                        ↓                                 │  │
│  │  ┌────────────────────────────────────────────────┐     │  │
│  │  │  Email Extractor (Regex)                       │     │  │
│  │  │  - Parse website text for email patterns       │     │  │
│  │  │  - Filter noise (example.com, etc.)            │     │  │
│  │  └────────────────────────────────────────────────┘     │  │
│  │                        ↓                                 │  │
│  │  Result: {lead + research_summary + email}              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    WRITE PHASE                           │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────┐     │  │
│  │  │  Job DB (Ghost/PostgreSQL)                     │     │  │
│  │  │  INSERT INTO leads (                           │     │  │
│  │  │    lead_id, job_id, name, phone, email,        │     │  │
│  │  │    address, website, research_summary,         │     │  │
│  │  │    status='RESEARCHED'                         │     │  │
│  │  │  )                                              │     │  │
│  │  └────────────────────────────────────────────────┘     │  │
│  │                        ↓                                 │  │
│  │  ┌────────────────────────────────────────────────┐     │  │
│  │  │  Master DB (Ghost/PostgreSQL)                  │     │  │
│  │  │  UPDATE jobs                                    │     │  │
│  │  │  SET status = 'RESEARCH_COMPLETE'              │     │  │
│  │  │  WHERE job_id = ?                              │     │  │
│  │  └────────────────────────────────────────────────┘     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Output: {status: "success", leads_count: 10, job_id: "..."}   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Input
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "query": "plumbing in Austin TX",
  "job_connection_string": "postgresql://ghost:***@job-db.ghost.build/postgres",
  "lead_count": 10
}
```

### 2. Search Phase Output
```python
[
  {
    "name": "ABC Plumbing",
    "phone": "+1 512-555-0123",
    "address": "123 Main St, Austin, TX 78701",
    "website": "https://abcplumbing.com",
    "rating": 4.5,
    "email": None
  },
  # ... 9 more leads
]
```

### 3. Enrich Phase Output
```python
[
  {
    "name": "ABC Plumbing",
    "phone": "+1 512-555-0123",
    "address": "123 Main St, Austin, TX 78701",
    "website": "https://abcplumbing.com",
    "rating": 4.5,
    "email": "info@abcplumbing.com",
    "research_summary": "Family-owned plumbing service with 20+ years experience. Offers emergency repairs, installations, and maintenance. Website shows professional branding but lacks online booking - potential pain point for our scheduling SaaS."
  },
  # ... 9 more enriched leads
]
```

### 4. Write Phase Output
```sql
-- Job DB: leads table
lead_id                              | job_id                               | name          | status
-------------------------------------|--------------------------------------|---------------|------------
a1b2c3d4-e5f6-7890-abcd-ef1234567890 | 123e4567-e89b-12d3-a456-426614174000 | ABC Plumbing  | RESEARCHED
... (10 rows)

-- Master DB: jobs table
job_id                               | status             | created_at
-------------------------------------|--------------------|-----------
123e4567-e89b-12d3-a456-426614174000 | RESEARCH_COMPLETE  | 2024-01-15 10:30:00
```

## Module Responsibilities

### `agent.py` - Orchestrator
- Entry point for the agent
- Coordinates search → enrich → write pipeline
- Error handling and logging
- Status updates
- CLI interface

### `search.py` - Lead Discovery
- Google Maps API integration
- Text search for businesses
- Place Details enrichment
- Business status filtering
- Rate limiting

### `enrich.py` - AI Enhancement
- Website content scraping
- Claude API integration
- Business analysis
- Email extraction
- Summary generation

### `writer.py` - Persistence
- Database connection management
- Lead insertion
- Job status updates
- Transaction handling

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Error Scenarios                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Google Maps API Failure                                    │
│  ├─ REQUEST_DENIED → ValueError("Invalid API key")          │
│  ├─ ZERO_RESULTS → Return empty list                        │
│  └─ OVER_QUERY_LIMIT → Retry with backoff                   │
│                                                             │
│  Website Scraping Failure                                   │
│  ├─ Timeout → Use placeholder text                          │
│  ├─ 404/500 → Use placeholder text                          │
│  └─ Invalid HTML → Use placeholder text                     │
│                                                             │
│  Claude API Failure                                         │
│  ├─ Rate limit → Retry with backoff                         │
│  ├─ Invalid API key → Raise exception                       │
│  └─ Timeout → Retry once                                    │
│                                                             │
│  Database Failure                                           │
│  ├─ Connection error → Raise exception                      │
│  ├─ Constraint violation → Log and continue                 │
│  └─ Transaction error → Rollback and raise                  │
│                                                             │
│  All Failures                                               │
│  └─ Update job status to RESEARCH_FAILED                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Performance Characteristics

### Sequential Processing (Current)
```
Lead 1: [Search 0.5s] → [Scrape 1.5s] → [Claude 2.5s] → [Write 0.05s] = 4.55s
Lead 2: [Search 0.5s] → [Scrape 1.5s] → [Claude 2.5s] → [Write 0.05s] = 4.55s
...
Lead 10: [Search 0.5s] → [Scrape 1.5s] → [Claude 2.5s] → [Write 0.05s] = 4.55s

Total: ~45s for 10 leads
```

### Parallel Processing (Optimized)
```
Search Phase: [10 leads × 0.5s] = 5s (sequential due to API)

Enrich Phase (parallel):
├─ Lead 1: [Scrape 1.5s] → [Claude 2.5s] = 4s
├─ Lead 2: [Scrape 1.5s] → [Claude 2.5s] = 4s
├─ ...
└─ Lead 10: [Scrape 1.5s] → [Claude 2.5s] = 4s
All parallel: ~4s

Write Phase: [10 leads × 0.05s] = 0.5s (batched)

Total: ~10s for 10 leads (4.5x speedup)
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TrueFoundry Job                          │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Container: research-agent:latest                     │ │
│  │  ├─ Python 3.11                                       │ │
│  │  ├─ Dependencies (httpx, anthropic, asyncpg, etc.)    │ │
│  │  └─ Entrypoint: python entrypoint.py                  │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↓                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Environment Variables                                │ │
│  │  ├─ JOB_ID (from Orchestrator)                        │ │
│  │  ├─ QUERY (from Orchestrator)                         │ │
│  │  ├─ JOB_CONNECTION_STRING (from Orchestrator)         │ │
│  │  ├─ LEAD_COUNT (from Orchestrator)                    │ │
│  │  ├─ MASTER_DATABASE_URL (from Secret)                 │ │
│  │  ├─ GOOGLE_MAPS_API_KEY (from Secret)                 │ │
│  │  └─ ANTHROPIC_API_KEY (from Secret)                   │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↓                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  External Services                                    │ │
│  │  ├─ Google Maps API (places.googleapis.com)           │ │
│  │  ├─ Anthropic API (api.anthropic.com)                 │ │
│  │  ├─ Master Ghost DB (master-db.ghost.build)           │ │
│  │  └─ Job Ghost DB (job-{id}.ghost.build)               │ │
│  └───────────────────────────────────────────────────────┘ │
│                           ↓                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Outputs                                              │ │
│  │  ├─ Logs → TrueFoundry Dashboard                      │ │
│  │  ├─ Metrics → Prometheus (optional)                   │ │
│  │  └─ Exit Code → Orchestrator                          │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Integration with Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    Full Pipeline                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Slack Bot                                               │
│     └─ User: "@agent find 10 plumbing leads in Austin TX"  │
│                           ↓                                 │
│  2. Orchestrator                                            │
│     ├─ Creates job in master DB (status: INITIATED)        │
│     ├─ Creates per-job Ghost DB                            │
│     └─ Triggers Research Agent                             │
│                           ↓                                 │
│  3. Research Agent ← YOU ARE HERE                           │
│     ├─ Searches Google Maps                                │
│     ├─ Enriches with Claude                                │
│     ├─ Saves to job DB                                     │
│     └─ Updates status: RESEARCH_COMPLETE                   │
│                           ↓                                 │
│  4. Strategy Agent (TODO)                                   │
│     ├─ Reads leads from job DB                             │
│     ├─ Generates call scripts                              │
│     ├─ Generates email templates                           │
│     └─ Posts to Slack for approval                         │
│                           ↓                                 │
│  5. Human Approval Gate                                     │
│     └─ Slack: CONFIRM or REVISE                            │
│                           ↓                                 │
│  6. Outreach Agent (TODO)                                   │
│     ├─ Calls leads via Bland AI                            │
│     └─ Updates lead status                                 │
│                           ↓                                 │
│  7. Follow-up Agent (TODO)                                  │
│     └─ Sends emails via Gmail API                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema Details

### Master DB

```sql
-- Table: jobs
CREATE TABLE jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'INITIATED',
    db_connection_string TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Status flow:
-- INITIATED → RESEARCH_COMPLETE → STRATEGY_COMPLETE → 
-- AWAITING_APPROVAL → APPROVED → OUTREACH_COMPLETE

-- Indexes:
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
```

### Job DB (per-job)

```sql
-- Table: leads
CREATE TABLE leads (
    lead_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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

-- Status flow:
-- RESEARCHED → ACCEPTED/DENIED/UNANSWERED → EMAIL_SENT

-- Indexes:
CREATE INDEX idx_leads_job_id ON leads(job_id);
CREATE INDEX idx_leads_status ON leads(status);
```

## Monitoring & Observability

### Logs
```
🔍 Research Agent started for job 123e4567-e89b-12d3-a456-426614174000
📝 Query: plumbing in Austin TX

🌍 Searching for 10 leads...
✅ Found 10 leads

🧠 Enriching leads with Claude...
  [1/10] Enriching ABC Plumbing...
  [2/10] Enriching XYZ Plumbing...
  ...
✅ Enriched 10 leads

💾 Saving leads to Ghost DB...
✅ Saved 10 leads to job DB

📊 Updating job status...
✅ Updated job status to RESEARCH_COMPLETE

✅ Research Agent completed successfully!
📈 Summary: 10 leads researched and saved
```

### Metrics (Future)
- `research_agent_duration_seconds` - Total execution time
- `research_agent_leads_found` - Number of leads discovered
- `research_agent_leads_enriched` - Number successfully enriched
- `research_agent_api_calls_total` - API call count by service
- `research_agent_errors_total` - Error count by type
- `research_agent_cost_dollars` - Estimated cost per run

## Security Considerations

1. **API Keys**: Stored in TrueFoundry secrets, never in code
2. **Database Credentials**: Connection strings from environment
3. **Input Validation**: Query sanitization to prevent injection
4. **Rate Limiting**: Respect API quotas and limits
5. **Error Messages**: Don't leak sensitive info in logs
6. **Network**: HTTPS only for all external calls

## Scalability

### Current Limits
- 10 leads: ~45s (sequential)
- 100 leads: ~7.5 minutes (sequential)
- 1000 leads: ~75 minutes (sequential)

### Optimization Strategies
1. **Parallel enrichment**: 4-5x speedup
2. **Batch API calls**: Reduce network overhead
3. **Caching**: Reuse website scrapes
4. **Distributed**: Multiple agent instances
5. **Queue-based**: Process leads asynchronously

### Cost at Scale
- 1,000 leads/day: ~$18/day
- 10,000 leads/day: ~$180/day
- 100,000 leads/day: ~$1,800/day
