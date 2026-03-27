import asyncpg
import uuid
from typing import List, Dict

async def save_leads(job_id: str, leads: List[Dict], connection_string: str):
    """
    Saves enriched leads to the per-job Ghost database.
    
    Args:
        job_id: UUID of the job
        leads: List of enriched lead dicts
        connection_string: PostgreSQL connection string for the job DB
    """
    # Connect to job-specific Ghost DB
    conn = await asyncpg.connect(connection_string)
    
    try:
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
        await conn.close()


async def update_job_status(job_id: str, status: str, master_connection_string: str):
    """
    Updates job status in the master Ghost database.
    
    Args:
        job_id: UUID of the job
        status: New status (e.g., "RESEARCH_COMPLETE")
        master_connection_string: PostgreSQL connection string for master DB
    """
    conn = await asyncpg.connect(master_connection_string)
    
    try:
        await conn.execute(
            """
            UPDATE jobs 
            SET status = $1 
            WHERE job_id = $2
            """,
            status,
            uuid.UUID(job_id)
        )
        
        print(f"✅ Updated job {job_id} status to {status}")
        
    finally:
        await conn.close()
