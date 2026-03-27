# Research Agent Integration Guide

How to integrate the Research Agent with the Orchestrator and TrueFoundry.

## Orchestrator Integration

The Orchestrator triggers the Research Agent as the first step in the pipeline.

### Example: Orchestrator Code

```python
import asyncio
import asyncpg
import uuid
import os
from truefoundry.deploy import trigger_job

async def trigger_research_agent(job_id: str, query: str):
    """
    Orchestrator triggers Research Agent on TrueFoundry.
    """
    # 1. Create per-job Ghost DB
    job_db_connection_string = await create_ghost_db(f"job-{job_id}")
    
    # 2. Update master job with connection string
    master_conn = await asyncpg.connect(os.getenv("MASTER_DATABASE_URL"))
    await master_conn.execute(
        "UPDATE jobs SET db_connection_string = $1 WHERE job_id = $2",
        job_db_connection_string,
        uuid.UUID(job_id)
    )
    await master_conn.close()
    
    # 3. Trigger Research Agent job on TrueFoundry
    job_response = await trigger_job(
        job_name="research-agent",
        env_vars={
            "JOB_ID": job_id,
            "QUERY": query,
            "JOB_CONNECTION_STRING": job_db_connection_string,
            "LEAD_COUNT": "10",
            "MASTER_DATABASE_URL": os.getenv("MASTER_DATABASE_URL"),
            "HASDATA_API_KEY": os.getenv("HASDATA_API_KEY"),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        }
    )
    
    print(f"✅ Research Agent triggered: {job_response['job_id']}")
    return job_response


async def create_ghost_db(db_name: str) -> str:
    """
    Creates a new Ghost DB for this job.
    
    In production, use Ghost CLI:
        ghost create --name {db_name}
        ghost connect {db_id}
    
    Returns connection string.
    """
    # Placeholder - implement Ghost DB creation
    # For now, return master DB (not recommended for production)
    return os.getenv("MASTER_DATABASE_URL")
```

## TrueFoundry Deployment

### 1. Build Docker Image

```bash
docker build -f deploy/Dockerfile.research -t research-agent:latest .
```

### 2. Push to Registry

```bash
docker tag research-agent:latest registry.truefoundry.com/your-org/research-agent:latest
docker push registry.truefoundry.com/your-org/research-agent:latest
```

### 3. Deploy Job

Using `truefoundry.yaml`:

```yaml
name: research-agent
type: job
image: registry.truefoundry.com/your-org/research-agent:latest

resources:
  cpu: 1
  memory: 2Gi

env:
  - name: MASTER_DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: ghost-credentials
        key: master_db_url
  
  - name: HASDATA_API_KEY
    valueFrom:
      secretKeyRef:
        name: api-keys
        key: hasdata
  
  - name: OPENAI_API_KEY
    valueFrom:
      secretKeyRef:
        name: api-keys
        key: openai

# These are set dynamically by Orchestrator
# - JOB_ID
# - QUERY
# - JOB_CONNECTION_STRING
# - LEAD_COUNT
```

Deploy:

```bash
tfy deploy --file deploy/truefoundry.yaml
```

## Monitoring

### TrueFoundry Dashboard

View live logs:

```
🔍 Research Agent started for job 123e4567-e89b-12d3-a456-426614174000
📝 Query: plumbing in Austin TX

🌍 Searching for 10 leads...
✅ Found 10 leads

🧠 Enriching leads with OpenAI...
  [1/10] Enriching ABC Plumbing...
  ...
```

### Database Monitoring

Query job status:

```sql
-- Check job status
SELECT job_id, status, created_at 
FROM jobs 
WHERE job_id = '123e4567-e89b-12d3-a456-426614174000';

-- Check leads
SELECT COUNT(*), status 
FROM leads 
WHERE job_id = '123e4567-e89b-12d3-a456-426614174000'
GROUP BY status;
```

## Error Handling

### Retry Logic

The Orchestrator should implement retry logic:

```python
async def run_research_with_retry(job_id: str, query: str, max_retries: int = 3):
    """
    Retry research agent on failure.
    """
    for attempt in range(max_retries):
        try:
            result = await trigger_research_agent(job_id, query)
            
            # Poll for completion
            while True:
                status = await get_job_status(job_id)
                
                if status == "RESEARCH_COMPLETE":
                    return result
                elif status == "RESEARCH_FAILED":
                    raise Exception("Research agent failed")
                
                await asyncio.sleep(5)
                
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            print(f"⚠️ Attempt {attempt + 1} failed, retrying...")
            await asyncio.sleep(10 * (attempt + 1))  # Exponential backoff
```

### Status Transitions

```
INITIATED → RESEARCH_COMPLETE (success)
INITIATED → RESEARCH_FAILED (error)
```

## Testing Integration

### Local Test

```python
# test_integration.py
import asyncio
from agents.research.agent import run_research_agent

async def test():
    result = await run_research_agent(
        job_id="test-123",
        query="coffee shops in Seattle",
        job_connection_string="postgresql://...",
        lead_count=3
    )
    print(result)

asyncio.run(test())
```

### TrueFoundry Test

```bash
# Trigger job manually
tfy job trigger research-agent \
  --env JOB_ID=test-123 \
  --env QUERY="coffee shops in Seattle" \
  --env JOB_CONNECTION_STRING="postgresql://..." \
  --env LEAD_COUNT=3

# View logs
tfy logs research-agent --follow
```

## Performance Tuning

### Parallel Enrichment

For faster processing, enrich leads in parallel:

```python
# In agent.py, replace sequential enrichment with:
import asyncio

enriched_leads = await asyncio.gather(*[
    enrich.enrich_lead(lead) 
    for lead in leads
])
```

This reduces 10-lead processing from ~60s to ~15s.

### Rate Limiting

HasData and OpenAI may enforce rate limits. Add throttling or backoff around `search.find_leads` and `enrich.enrich_lead` if you hit quotas.

## Next Steps

After Research Agent completes:

1. Orchestrator detects `RESEARCH_COMPLETE` status
2. Orchestrator triggers Strategy Agent with same `job_id`
3. Strategy Agent reads leads from job DB
4. Strategy Agent generates call scripts + email templates
5. Human approval gate via Slack
6. Outreach Agent executes calls

## Support

- TrueFoundry docs: https://docs.truefoundry.com
- Ghost DB docs: https://ghost.build/docs
- HasData: https://hasdata.com (API docs for Google Maps scrape endpoints)
- OpenAI API: https://platform.openai.com/docs
