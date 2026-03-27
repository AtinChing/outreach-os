import time
from pathlib import Path

import asyncpg

from agents.research import agent as research_agent
from backend.ghost_mcp import ghost_create_database, ghost_fork_database
from db.client import get_master_pool
from db.failure_detail import format_failure

REPO_ROOT = Path(__file__).resolve().parent.parent
JOB_SCHEMA_SQL = (REPO_ROOT / "db" / "job_schema.sql").read_text()


async def _apply_job_schema(connection_string: str) -> None:
    conn = await asyncpg.connect(connection_string)
    try:
        await conn.execute(JOB_SCHEMA_SQL)
    finally:
        await conn.close()


async def trigger_research(job_id: str) -> None:
    try:
        short_id = str(job_id)[:8]
        t0 = time.perf_counter()
        created = await ghost_create_database(name=f"job-{short_id}", wait=True)
        provisioning_ms = int((time.perf_counter() - t0) * 1000)

        connection_string = created["connection_string"]
        ghost_db_id = created["id"]

        await _apply_job_schema(connection_string)

        pool = await get_master_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE jobs
                SET db_connection_string = $1,
                    ghost_db_id = $2,
                    provisioning_ms = $3
                WHERE job_id = $4
                """,
                connection_string,
                ghost_db_id,
                provisioning_ms,
                job_id,
            )

        await research_agent.main(job_id, connection_string)

    except Exception as exc:
        detail = format_failure(exc)
        pool = await get_master_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE jobs SET status='FAILED', error_detail=$2 WHERE job_id=$1",
                job_id,
                detail,
            )
        raise exc


async def trigger_research_on_forked_db(job_id: str, connection_string: str) -> None:
    """Run research against an existing per-job DB (e.g. after Ghost fork)."""
    try:
        pool = await get_master_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE jobs SET status = $1, error_detail = NULL WHERE job_id = $2",
                "INITIATED",
                job_id,
            )
        await research_agent.main(job_id, connection_string)
    except Exception as exc:
        detail = format_failure(exc)
        pool = await get_master_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE jobs SET status='FAILED', error_detail=$2 WHERE job_id=$1",
                job_id,
                detail,
            )
        raise exc


async def fork_job_database(
    *,
    parent_job_id: str,
    new_job_id: str,
    parent_query: str,
    parent_ghost_db_id: str,
) -> tuple[str, str, int]:
    """
    Fork parent's Ghost DB via MCP; returns (connection_string, ghost_db_id, provisioning_ms).
    Caller inserts the new job row and schedules trigger_research_on_forked_db.
    """
    short_id = str(new_job_id)[:8]
    t0 = time.perf_counter()
    forked = await ghost_fork_database(
        source_id=parent_ghost_db_id,
        name=f"job-{short_id}-fork",
        wait=True,
    )
    provisioning_ms = int((time.perf_counter() - t0) * 1000)
    return forked["connection_string"], forked["id"], provisioning_ms
