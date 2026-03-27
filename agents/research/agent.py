import os
import asyncio
from dotenv import load_dotenv
from . import search, enrich, writer
from db.client import get_master_pool
from db.failure_detail import format_failure

load_dotenv()


async def main(job_id: str, connection_string: str):
    """
    Research Agent main entry point.
    
    This is the canonical function called by the orchestrator.
    
    Flow:
    1. Reads job query from master DB using job_id
    2. Calls Google Maps API via search.py to find leads
    3. Enriches each lead with OpenAI via enrich.py
    4. Saves leads to job-specific Ghost DB via writer.py
    5. Updates master job status to RESEARCH_COMPLETE
    
    Args:
        job_id: UUID of the job from master DB
        connection_string: PostgreSQL connection string for job-specific DB
    """
    print(f"🔍 Research Agent started for job {job_id}")
    
    try:
        # Step 1: Read query from master DB
        print(f"\n📋 Reading job details from master DB...")
        pool = await get_master_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT query FROM jobs WHERE job_id = $1",
                job_id
            )
        
        if not row:
            raise ValueError(f"Job {job_id} not found in master DB")
        
        query = row['query']
        print(f"📝 Query: {query}")
        
        # Step 2: Find leads via Google Maps API
        lead_count = 10  # Default lead count
        print(f"\n🌍 Searching for {lead_count} leads...")
        leads = await search.find_leads(query, count=lead_count)
        print(f"✅ Found {len(leads)} leads")
        
        # Step 3: Enrich each lead with OpenAI
        print(f"\n🧠 Enriching leads with OpenAI...")
        enriched_leads = []
        for i, lead in enumerate(leads, 1):
            print(f"  [{i}/{len(leads)}] Enriching {lead.get('name')}...")
            enriched = await enrich.enrich_lead(lead)
            enriched_leads.append(enriched)
        print(f"✅ Enriched {len(enriched_leads)} leads")
        
        # Step 4: Save to job-specific Ghost DB
        print(f"\n💾 Saving leads to Ghost DB...")
        await writer.save_leads(job_id, enriched_leads, connection_string)
        
        # Step 5: Update master job status to RESEARCH_COMPLETE
        print(f"\n📊 Updating job status...")
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE jobs
                SET status = $1,
                    error_detail = NULL,
                    research_completed_at = NOW()
                WHERE job_id = $2
                """,
                "RESEARCH_COMPLETE",
                job_id,
            )
        print(f"✅ Updated job status to RESEARCH_COMPLETE")
        
        print(f"\n✅ Research Agent completed successfully!")
        print(f"📈 Summary: {len(enriched_leads)} leads researched and saved")
        
        return {
            "status": "success",
            "leads_count": len(enriched_leads),
            "job_id": job_id
        }
        
    except Exception as e:
        print(f"\n❌ Research Agent failed: {str(e)}")
        
        # Update job status to FAILED
        try:
            detail = format_failure(e)
            pool = await get_master_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE jobs SET status = $1, error_detail = $2 WHERE job_id = $3",
                    "FAILED",
                    detail,
                    job_id,
                )
            print(f"✅ Updated job status to FAILED")
        except Exception as status_error:
            print(f"⚠️  Failed to update job status: {str(status_error)}")
        
        raise


# CLI entry point for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python agent.py <job_id> <job_connection_string>")
        print('Example: python agent.py "123e4567-e89b-12d3-a456-426614174000" "postgresql://..."')
        sys.exit(1)
    
    job_id = sys.argv[1]
    job_connection_string = sys.argv[2]
    
    asyncio.run(main(job_id, job_connection_string))
