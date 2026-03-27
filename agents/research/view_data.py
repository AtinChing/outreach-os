#!/usr/bin/env python3
"""
View persisted data from Ghost DB.

Usage:
    python3 view_data.py [job_id]
    
Examples:
    python3 view_data.py                           # Show all jobs and recent leads
    python3 view_data.py ae323a31-545e-41db-afae-417257f597f7  # Show specific job
"""

import asyncio
import asyncpg
import os
import sys
from dotenv import load_dotenv

load_dotenv()

async def view_data(job_id: str = None):
    master_db_url = os.getenv("MASTER_DATABASE_URL")
    if not master_db_url:
        raise ValueError("MASTER_DATABASE_URL not set")
    
    conn = await asyncpg.connect(master_db_url)
    
    try:
        if job_id:
            # Show specific job
            print(f"🔍 Viewing Job: {job_id}\n")
            
            job = await conn.fetchrow(
                "SELECT * FROM jobs WHERE job_id = $1",
                job_id
            )
            
            if not job:
                print(f"❌ Job {job_id} not found")
                return
            
            print(f"📊 Job Details:")
            print(f"   Status: {job['status']}")
            print(f"   Query: {job['query']}")
            print(f"   Created: {job['created_at']}\n")
            
            leads = await conn.fetch(
                "SELECT * FROM leads WHERE job_id = $1 ORDER BY created_at",
                job_id
            )
            
            print(f"📋 Leads: {len(leads)}\n")
            
            for i, lead in enumerate(leads, 1):
                print(f"   Lead {i}:")
                print(f"      Name: {lead['name']}")
                print(f"      Phone: {lead['phone']}")
                print(f"      Email: {lead['email']}")
                print(f"      Website: {lead['website']}")
                print(f"      Address: {lead['address']}")
                if lead['research_summary']:
                    summary = lead['research_summary']
                    if len(summary) > 150:
                        summary = summary[:150] + "..."
                    print(f"      Summary: {summary}")
                print()
        else:
            # Show all jobs
            print("📊 All Jobs:\n")
            
            jobs = await conn.fetch(
                "SELECT * FROM jobs ORDER BY created_at DESC LIMIT 10"
            )
            
            if not jobs:
                print("   No jobs found\n")
                return
            
            for job in jobs:
                lead_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM leads WHERE job_id = $1",
                    job['job_id']
                )
                
                print(f"   Job ID: {job['job_id']}")
                print(f"   Query: {job['query']}")
                print(f"   Status: {job['status']}")
                print(f"   Leads: {lead_count}")
                print(f"   Created: {job['created_at']}")
                print()
            
            print(f"\n💡 To view a specific job:")
            print(f"   python3 view_data.py <job_id>")
    
    finally:
        await conn.close()


if __name__ == "__main__":
    job_id = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(view_data(job_id))
