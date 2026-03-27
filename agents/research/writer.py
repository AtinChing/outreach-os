import asyncpg
import uuid
from typing import List, Dict
from db.client import get_job_pool


async def save_leads(job_id: str, leads: List[Dict], connection_string: str):
    """
    Saves enriched leads to the per-job Ghost database.
    
    Args:
        job_id: UUID of the job
        leads: List of enriched lead dicts
        connection_string: PostgreSQL connection string for the job DB
    """
    # Connect to job-specific Ghost DB
    pool = await get_job_pool(connection_string)
    
    try:
        async with pool.acquire() as conn:
            # Insert each lead
            for lead in leads:
                await conn.execute(
                    """
                    INSERT INTO leads (
                        lead_id, job_id, name, phone, email, 
                        address, website, research_summary, status
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    """,
                    uuid.uuid4(),
                    uuid.UUID(job_id),
                    lead.get("name"),
                    lead.get("phone"),
                    lead.get("email"),
                    lead.get("address"),
                    lead.get("website"),
                    lead.get("research_summary"),
                    "RESEARCHED"
                )
        
        print(f"✅ Saved {len(leads)} leads to job DB")
        
    finally:
        await pool.close()
