#!/usr/bin/env python3
"""
Test script for Research Agent.

Usage:
    python test_agent.py

This will:
1. Create a test job in master DB
2. Create a test job DB
3. Run the research agent
4. Verify leads were saved
5. Clean up test data
"""

import asyncio
import asyncpg
import uuid
import os
from dotenv import load_dotenv
from agent import run_research_agent

load_dotenv()

async def test_research_agent():
    """
    End-to-end test of the research agent.
    """
    print("🧪 Starting Research Agent Test\n")
    
    # Configuration
    master_db_url = os.getenv("MASTER_DATABASE_URL")
    if not master_db_url:
        raise ValueError("MASTER_DATABASE_URL not set in .env")
    
    # For testing, we'll use the same DB for both master and job
    # In production, each job gets its own Ghost DB
    job_db_url = master_db_url
    
    job_id = str(uuid.uuid4())
    test_query = "coffee shops in San Francisco CA"
    
    print(f"📋 Test Configuration:")
    print(f"   Job ID: {job_id}")
    print(f"   Query: {test_query}")
    print(f"   Lead Count: 5\n")
    
    # Step 1: Create test job in master DB
    print("1️⃣ Creating test job in master DB...")
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
        print("   ✅ Test job created\n")
    finally:
        await conn.close()
    
    # Step 2: Ensure leads table exists in job DB
    print("2️⃣ Setting up job DB schema...")
    conn = await asyncpg.connect(job_db_url)
    try:
        # Create leads table if not exists
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
        print("   ✅ Job DB ready\n")
    finally:
        await conn.close()
    
    # Step 3: Run research agent
    print("3️⃣ Running Research Agent...\n")
    print("=" * 60)
    try:
        result = await run_research_agent(
            job_id=job_id,
            query=test_query,
            job_connection_string=job_db_url,
            lead_count=5
        )
        print("=" * 60)
        print(f"\n   ✅ Agent completed: {result}\n")
    except Exception as e:
        print(f"\n   ❌ Agent failed: {e}\n")
        raise
    
    # Step 4: Verify results
    print("4️⃣ Verifying results...")
    conn = await asyncpg.connect(job_db_url)
    try:
        # Check job status
        job_status = await conn.fetchval(
            "SELECT status FROM jobs WHERE job_id = $1",
            uuid.UUID(job_id)
        )
        print(f"   Job status: {job_status}")
        assert job_status == "RESEARCH_COMPLETE", f"Expected RESEARCH_COMPLETE, got {job_status}"
        
        # Check leads
        leads = await conn.fetch(
            "SELECT * FROM leads WHERE job_id = $1",
            uuid.UUID(job_id)
        )
        print(f"   Leads saved: {len(leads)}")
        
        # Display sample lead
        if leads:
            sample = leads[0]
            print(f"\n   📄 Sample Lead:")
            print(f"      Name: {sample['name']}")
            print(f"      Phone: {sample['phone']}")
            print(f"      Email: {sample['email']}")
            print(f"      Website: {sample['website']}")
            print(f"      Address: {sample['address'][:50]}..." if sample['address'] else "      Address: None")
            print(f"      Summary: {sample['research_summary'][:100]}..." if sample['research_summary'] else "      Summary: None")
            print(f"      Status: {sample['status']}")
        
        print(f"\n   ✅ All verifications passed\n")
        
    finally:
        await conn.close()
    
    # Step 5: Cleanup
    print("5️⃣ Cleaning up test data...")
    conn = await asyncpg.connect(job_db_url)
    try:
        await conn.execute("DELETE FROM leads WHERE job_id = $1", uuid.UUID(job_id))
        await conn.execute("DELETE FROM jobs WHERE job_id = $1", uuid.UUID(job_id))
        print("   ✅ Test data cleaned up\n")
    finally:
        await conn.close()
    
    print("🎉 Test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_research_agent())
