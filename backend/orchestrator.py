import asyncio
import subprocess
import json
from db.client import get_master_pool
from agents.research import agent as research_agent

async def trigger_research(job_id: str):
    # Step 1: Create a new Ghost DB for this job
    result = subprocess.run(
        ["ghost", "create", "--name", f"job-{job_id}", "--json", "--wait"],
        capture_output=True,
        text=True
    )
    ghost_output = json.loads(result.stdout)

    # Step 2: Get the connection string for the new DB
    connect_result = subprocess.run(
        ["ghost", "connect", ghost_output["id"]],
        capture_output=True,
        text=True
    )
    connection_string = connect_result.stdout.strip()

    # Step 3: Initialize the leads table on the new per-job DB
    subprocess.run(
        ["ghost", "sql", ghost_output["id"]],
        input=open("db/job_schema.sql").read(),
        capture_output=True,
        text=True
    )

    # Step 4: Store connection string back into master jobs table
    pool = await get_master_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE jobs SET db_connection_string=$1 WHERE job_id=$2",
            connection_string,
            job_id
        )

    # Step 5: Kick off research agent with job_id + connection string
    await research_agent.main(job_id, connection_string)
