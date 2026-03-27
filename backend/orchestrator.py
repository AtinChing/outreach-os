import json
import subprocess
from pathlib import Path

from agents.research import agent as research_agent
from db.client import get_master_pool


async def trigger_research(job_id: str) -> None:
    try:
        # 1. Create a new Ghost DB for this job
        short_id = str(job_id)[:8]
        result = subprocess.run(
            ["ghost", "create", "--name", f"job-{short_id}", "--json", "--wait"],
            capture_output=True,
            text=True,
            check=True,
        )
        db_id = json.loads(result.stdout)["id"]

        # 2. Get the connection string
        result = subprocess.run(
            ["ghost", "connect", db_id],
            capture_output=True,
            text=True,
            check=True,
        )
        connection_string = result.stdout.strip()

        # 3. Initialize the leads table
        sql = Path("db/job_schema.sql").read_text()
        subprocess.run(
            ["ghost", "sql", db_id],
            input=sql,
            capture_output=True,
            text=True,
            check=True,
        )

        # 4. Store the connection string in the master DB
        pool = await get_master_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE jobs SET db_connection_string=$1 WHERE job_id=$2",
                connection_string,
                job_id,
            )

        # 5. Hand off to the research agent
        await research_agent.main(job_id, connection_string)

    except Exception as exc:
        pool = await get_master_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE jobs SET status='FAILED' WHERE job_id=$1",
                job_id,
            )
        raise exc
