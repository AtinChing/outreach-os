#!/usr/bin/env python3
"""
Test script that PERSISTS data in the database.

Usage:
    python3 test_persist.py [query] [lead_count]

Examples:
    python3 test_persist.py "plumbers in Austin TX" 10
    python3 test_persist.py "dentists in Miami FL"
    python3 test_persist.py

This will:
1. Create a test job in master DB
2. Run the research agent
3. Show results
4. KEEP the data in the database (no cleanup)
"""

import asyncio
import asyncpg
import uuid
import os
import sys
from dotenv import load_dotenv
from agent import run_research_agent

load_dotenv()

async def test_with_persistence(query: str = None, lead_count: int = 5):
    """
    End-to-end test that keeps data in the database.
    """
    print("🧪 Research Agent Test (with persistence)\n")
    
    # Configuration
    master_db_url = os.getenv("MASTER_DATABASE_URL")
    if not master_db_url:
        raise ValueError("MASTER_DATABASE_URL not set in .env")
    
    # For testing, we'll use the same DB for both master and job
    job_db_url = master_db_url
    
    job_id = str(uuid.uuid4())
    test_query = query or "coffee shops in San Francisco CA"
    
    print(f"📋 Configuration:")
    print(f"   Job ID: {job_id}")
    print(f"   Query: {test_query}")
    print(f"   Lead Count: {lead_count}\n")
    
    # Step 1: Create test job in master DB
    print("1️⃣ Creating job in master DB...")
    conn = await asyncpg.connect(master_db_url)
    try:
        await conn.execute(
            """
            INSERT INTO jobs (job_id, query, status, db_connection_string)
            VALUES ($1, $2, $3, $4)
            """,
            uuid.UUID(job_id),
            test_query,
            "INITIATED",
            job_db_url
        )
        print("   ✅ Job created\n")
    finally:
        await conn.close()
    
    # Step 2: Ensure leads table exists
    print("2️⃣ Setting up leads table...")
    conn = await asyncpg.connect(job_db_url)
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
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
            )
        """)
        print("   ✅ Table ready\n")
    finally:
        await conn.close()
    
    # Step 3: Run research agent
    print("3️⃣ Running Research Agent...\n")
    print("=" * 60)
    result = await run_research_agent(
        job_id=job_id,
        query=test_query,
        job_connection_string=job_db_url,
        lead_count=lead_count
    )
    print("=" * 60)
    print(f"\n✅ Agent completed: {result}\n")
    
    # Step 4: Display results
    print("4️⃣ Results (PERSISTED in database):\n")
    conn = await asyncpg.connect(job_db_url)
    try:
        # Show job
        job = await conn.fetchrow(
            "SELECT * FROM jobs WHERE job_id = $1",
            uuid.UUID(job_id)
        )
        print(f"📊 Job Status: {job['status']}")
        print(f"   Created: {job['created_at']}\n")
        
        # Show all leads
        leads = await conn.fetch(
            "SELECT * FROM leads WHERE job_id = $1 ORDER BY created_at",
            uuid.UUID(job_id)
        )
        print(f"📋 Leads Found: {len(leads)}\n")
        
        for i, lead in enumerate(leads, 1):
            print(f"   Lead {i}:")
            print(f"      Name: {lead['name']}")
            print(f"      Phone: {lead['phone']}")
            print(f"      Email: {lead['email']}")
            print(f"      Website: {lead['website']}")
            print(f"      Address: {lead['address']}")
            print(f"      Summary: {lead['research_summary'][:150]}..." if lead['research_summary'] and len(lead['research_summary']) > 150 else f"      Summary: {lead['research_summary']}")
            print(f"      Status: {lead['status']}")
            print()
        
    finally:
        await conn.close()
    
    print("=" * 60)
    print("✅ Data persisted in Ghost DB!")
    print(f"   Job ID: {job_id}")
    print(f"\n   To view in psql:")
    print(f"   ghost psql arxoiv5quf")
    print(f"   SELECT * FROM jobs WHERE job_id = '{job_id}';")
    print(f"   SELECT name, phone, website FROM leads WHERE job_id = '{job_id}';")
    print("=" * 60)


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else None
    lead_count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    asyncio.run(test_with_persistence(query, lead_count))
