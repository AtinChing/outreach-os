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
2. Run the research agent (reads query from master; default lead count is set in agent.py)
3. Show results
4. KEEP the data in the database (no cleanup)

Note: `lead_count` only affects display expectations; the agent uses a fixed default lead count internally.
"""

import asyncio
import asyncpg
import uuid
import os
import sys
from typing import Optional

from dotenv import load_dotenv

from agent import main

load_dotenv()


async def test_with_persistence(query: Optional[str] = None, lead_count: int = 5) -> None:
    print("🧪 Research Agent Test (with persistence)\n")

    master_db_url = os.getenv("MASTER_DATABASE_URL")
    if not master_db_url:
        raise ValueError("MASTER_DATABASE_URL not set in .env")

    job_db_url = master_db_url

    job_id = str(uuid.uuid4())
    test_query = query or "coffee shops in San Francisco CA"

    print(f"📋 Configuration:")
    print(f"   Job ID: {job_id}")
    print(f"   Query: {test_query}")
    print(f"   Requested lead count (info only): {lead_count}\n")

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
            job_db_url,
        )
        print("   ✅ Job created\n")
    finally:
        await conn.close()

    print("2️⃣ Setting up leads table...")
    conn = await asyncpg.connect(job_db_url)
    try:
        await conn.execute(
            """
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
            """
        )
        print("   ✅ Table ready\n")
    finally:
        await conn.close()

    print("3️⃣ Running Research Agent...\n")
    print("=" * 60)
    result = await main(job_id, job_db_url)
    print("=" * 60)
    print(f"\n✅ Agent completed: {result}\n")

    print("4️⃣ Results (PERSISTED in database):\n")
    conn = await asyncpg.connect(job_db_url)
    try:
        job = await conn.fetchrow(
            "SELECT * FROM jobs WHERE job_id = $1",
            uuid.UUID(job_id),
        )
        print(f"📊 Job Status: {job['status']}")
        print(f"   Created: {job['created_at']}\n")

        leads = await conn.fetch(
            "SELECT * FROM leads WHERE job_id = $1 ORDER BY created_at",
            uuid.UUID(job_id),
        )
        print(f"📋 Leads Found: {len(leads)}\n")

        for i, lead in enumerate(leads, 1):
            print(f"   Lead {i}:")
            print(f"      Name: {lead['name']}")
            print(f"      Phone: {lead['phone']}")
            print(f"      Email: {lead['email']}")
            print(f"      Website: {lead['website']}")
            print(f"      Address: {lead['address']}")
            if lead["research_summary"] and len(lead["research_summary"]) > 150:
                print(f"      Summary: {lead['research_summary'][:150]}...")
            else:
                print(f"      Summary: {lead['research_summary']}")
            print(f"      Status: {lead['status']}")
            print()

    finally:
        await conn.close()

    print("=" * 60)
    print("✅ Data persisted in Ghost DB!")
    print(f"   Job ID: {job_id}")
    print(f"\n   To view in psql, connect with MASTER_DATABASE_URL and run:")
    print(f"   SELECT * FROM jobs WHERE job_id = '{job_id}';")
    print(f"   SELECT name, phone, website FROM leads WHERE job_id = '{job_id}';")
    print("=" * 60)


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else None
    lc = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    asyncio.run(test_with_persistence(q, lc))
