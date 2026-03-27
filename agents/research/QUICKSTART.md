# Research Agent Quick Start

Get the Research Agent running in 5 minutes.

## Prerequisites

1. Python 3.11+
2. Ghost DB (or any PostgreSQL database)
3. Google Maps API key
4. Anthropic API key

## Setup

### 1. Install Dependencies

```bash
cd agents/research
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` in project root:

```bash
# Master Ghost DB
MASTER_DATABASE_URL=postgresql://user:pass@host:5432/dbname

# API Keys
GOOGLE_MAPS_API_KEY=AIzaSy...
GEMINI_API_KEY=AIzaSy...  # Free tier available!
```

### 3. Initialize Database

Run the schema scripts:

```bash
# Master DB (run once)
psql $MASTER_DATABASE_URL < db/master_schema.sql

# Job DB (run once per job, or use same DB for testing)
psql $MASTER_DATABASE_URL < db/job_schema.sql
```

## Run Test

```bash
cd agents/research
python test_agent.py
```

Expected output:

```
🧪 Starting Research Agent Test

📋 Test Configuration:
   Job ID: 123e4567-e89b-12d3-a456-426614174000
   Query: coffee shops in San Francisco CA
   Lead Count: 5

1️⃣ Creating test job in master DB...
   ✅ Test job created

2️⃣ Setting up job DB schema...
   ✅ Job DB ready

3️⃣ Running Research Agent...
============================================================
🔍 Research Agent started for job 123e4567-e89b-12d3-a456-426614174000
📝 Query: coffee shops in San Francisco CA

🌍 Searching for 5 leads...
✅ Found 5 leads

🧠 Enriching leads with Claude...
  [1/5] Enriching Blue Bottle Coffee...
  [2/5] Enriching Sightglass Coffee...
  ...
✅ Enriched 5 leads

💾 Saving leads to Ghost DB...
✅ Saved 5 leads to job DB

📊 Updating job status...
✅ Updated job 123e4567-e89b-12d3-a456-426614174000 status to RESEARCH_COMPLETE

✅ Research Agent completed successfully!
📈 Summary: 5 leads researched and saved
============================================================

   ✅ Agent completed: {'status': 'success', 'leads_count': 5, 'job_id': '...'}

4️⃣ Verifying results...
   Job status: RESEARCH_COMPLETE
   Leads saved: 5

   📄 Sample Lead:
      Name: Blue Bottle Coffee
      Phone: +1 415-555-0123
      Email: info@bluebottlecoffee.com
      Website: https://bluebottlecoffee.com
      Address: 66 Mint St, San Francisco, CA 94103...
      Summary: Specialty coffee roaster with multiple locations. High-end...
      Status: RESEARCHED

   ✅ All verifications passed

5️⃣ Cleaning up test data...
   ✅ Test data cleaned up

🎉 Test completed successfully!
```

## Manual Run

```bash
python agent.py \
  "$(uuidgen)" \
  "plumbing in Austin TX" \
  "$MASTER_DATABASE_URL" \
  10
```

## Troubleshooting

### Google Maps API Error

```
ValueError: Google Maps API error: REQUEST_DENIED
```

**Solution**: Enable Places API in Google Cloud Console and check API key permissions.

### Claude API Error

```
anthropic.AuthenticationError: Invalid API key
```

**Solution**: Verify `ANTHROPIC_API_KEY` in `.env` starts with `sk-ant-api03-`.

### Gemini API Error

```
google.api_core.exceptions.PermissionDenied: API key not valid
```

**Solution**: 
- Verify `GEMINI_API_KEY` in `.env` starts with `AIza`
- Enable Generative Language API in Google Cloud Console
- See `GEMINI_SETUP.md` for detailed setup

### Database Connection Error

```
asyncpg.exceptions.InvalidCatalogNameError: database "postgres" does not exist
```

**Solution**: Check `MASTER_DATABASE_URL` format and database exists.

### No Leads Found

```
✅ Found 0 leads
```

**Solution**: Try a more specific query like "plumbers in Austin TX" instead of just "plumbing".

## Next Steps

1. Deploy to TrueFoundry (see `deploy/truefoundry.yaml`)
2. Integrate with Orchestrator
3. Connect to Strategy Agent

## API Reference

### `run_research_agent()`

```python
async def run_research_agent(
    job_id: str,           # UUID of job from master DB
    query: str,            # Natural language query
    job_connection_string: str,  # PostgreSQL connection string
    lead_count: int = 10   # Number of leads to find
) -> dict:
    """
    Returns:
        {
            "status": "success",
            "leads_count": 10,
            "job_id": "..."
        }
    """
```

### Query Format

Natural language queries work best:

✅ Good:
- "plumbing companies in Austin TX"
- "coffee shops in San Francisco"
- "dentists in Brooklyn NY"

❌ Bad:
- "plumbing" (too vague)
- "Austin TX" (no business type)
- "find me leads" (no specifics)
