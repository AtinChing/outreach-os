import os
import asyncio
from dotenv import load_dotenv
from agents.research import search, enrich, writer

load_dotenv()

async def run_research_agent(
    job_id: str, 
    query: str, 
    job_connection_string: str,
    lead_count: int = 10
):
    """
    Research Agent main entry point.
    
    Flow:
    1. Receives job_id + query from Orchestrator
    2. Calls Google Maps API via search.py to find leads
    3. Enriches each lead with Claude via enrich.py
    4. Saves leads to job-specific Ghost DB via writer.py
    5. Updates master job status to RESEARCH_COMPLETE
    
    Args:
        job_id: UUID of the job from master DB
        query: Natural language query (e.g., "10 plumbing leads in Austin TX")
        job_connection_string: PostgreSQL connection string for job-specific DB
        lead_count: Number of leads to find (default 10)
    """
    print(f"🔍 Research Agent started for job {job_id}")
    print(f"📝 Query: {query}")
    
    try:
        # Step 1: Find leads via Google Maps API
        print(f"\n🌍 Searching for {lead_count} leads...")
        leads = await search.find_leads(query, count=lead_count)
        print(f"✅ Found {len(leads)} leads")
        
        # Step 2: Enrich each lead with Claude
        print(f"\n🧠 Enriching leads with Claude...")
        enriched_leads = []
        for i, lead in enumerate(leads, 1):
            print(f"  [{i}/{len(leads)}] Enriching {lead.get('name')}...")
            enriched = await enrich.enrich_lead(lead)
            enriched_leads.append(enriched)
        print(f"✅ Enriched {len(enriched_leads)} leads")
        
        # Step 3: Save to job-specific Ghost DB
        print(f"\n💾 Saving leads to Ghost DB...")
        await writer.save_leads(job_id, enriched_leads, job_connection_string)
        
        # Step 4: Update master job status
        print(f"\n📊 Updating job status...")
        master_connection_string = os.getenv("MASTER_DATABASE_URL")
        if not master_connection_string:
            raise ValueError("MASTER_DATABASE_URL not set")
        
        await writer.update_job_status(
            job_id, 
            "RESEARCH_COMPLETE", 
            master_connection_string
        )
        
        print(f"\n✅ Research Agent completed successfully!")
        print(f"📈 Summary: {len(enriched_leads)} leads researched and saved")
        
        return {
            "status": "success",
            "leads_count": len(enriched_leads),
            "job_id": job_id
        }
        
    except Exception as e:
        print(f"\n❌ Research Agent failed: {str(e)}")
        
        # Update job status to failed
        try:
            master_connection_string = os.getenv("MASTER_DATABASE_URL")
            if master_connection_string:
                await writer.update_job_status(
                    job_id, 
                    "RESEARCH_FAILED", 
                    master_connection_string
                )
        except:
            pass
        
        raise


# CLI entry point for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python agent.py <job_id> <query> <job_connection_string> [lead_count]")
        print('Example: python agent.py "123e4567-e89b-12d3-a456-426614174000" "plumbing in Austin TX" "postgresql://..." 10')
        sys.exit(1)
    
    job_id = sys.argv[1]
    query = sys.argv[2]
    job_connection_string = sys.argv[3]
    lead_count = int(sys.argv[4]) if len(sys.argv) > 4 else 10
    
    asyncio.run(run_research_agent(job_id, query, job_connection_string, lead_count))
