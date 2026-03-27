#!/usr/bin/env python3
"""
Simple example of using the Research Agent.

Creates a job row in the master DB, then runs `main` (the agent reads the query from master).
"""

import asyncio
import os
import uuid

import asyncpg
from dotenv import load_dotenv

from agent import main

load_dotenv()


async def example_usage() -> None:
    master_url = os.getenv("MASTER_DATABASE_URL")
    if not master_url:
        raise ValueError("MASTER_DATABASE_URL not set in .env")

    job_id = str(uuid.uuid4())
    query = "coffee shops in Seattle WA"
    job_connection_string = master_url

    print("🚀 Starting Research Agent")
    print(f"   Job ID: {job_id}")
    print(f"   Query: {query}\n")

    conn = await asyncpg.connect(master_url)
    try:
        await conn.execute(
            """
            INSERT INTO jobs (job_id, query, status, db_connection_string)
            VALUES ($1, $2, $3, $4)
            """,
            uuid.UUID(job_id),
            query,
            "INITIATED",
            job_connection_string,
        )
    finally:
        await conn.close()

    conn = await asyncpg.connect(job_connection_string)
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
    finally:
        await conn.close()

    try:
        result = await main(job_id, job_connection_string)
        print(f"\n✅ Success!")
        print(f"   Status: {result['status']}")
        print(f"   Leads Found: {result['leads_count']}")
        print(f"   Job ID: {result['job_id']}")
        print(f"\n💡 To view the leads, run:")
        print(f"   SELECT * FROM leads WHERE job_id = '{job_id}';")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(example_usage())
