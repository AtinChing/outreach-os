import os
import asyncpg
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# Module-level pool cache
_master_pool: asyncpg.Pool | None = None
_job_pools: dict[str, asyncpg.Pool] = {}
_master_jobs_schema_ensured: bool = False


async def _ensure_master_jobs_schema(pool: asyncpg.Pool) -> None:
    """Idempotent ALTERs so older DBs match current API (avoids GET /jobs 500)."""
    global _master_jobs_schema_ensured
    if _master_jobs_schema_ensured:
        return
    async with pool.acquire() as conn:
        await conn.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS error_detail TEXT")
        await conn.execute(
            "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS parent_job_id UUID REFERENCES jobs(job_id)"
        )
        await conn.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS ghost_db_id TEXT")
        await conn.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS provisioning_ms INTEGER")
        await conn.execute(
            "ALTER TABLE jobs ADD COLUMN IF NOT EXISTS research_completed_at TIMESTAMP"
        )
    _master_jobs_schema_ensured = True


async def get_master_pool() -> asyncpg.Pool:
    global _master_pool
    if _master_pool is None:
        url = os.getenv("MASTER_DATABASE_URL")
        _master_pool = await asyncpg.create_pool(url)
        await _ensure_master_jobs_schema(_master_pool)
    return _master_pool


async def get_job_pool(connection_string: str) -> asyncpg.Pool:
    existing = _job_pools.get(connection_string)
    if existing is not None and not getattr(existing, "_closed", False):
        return existing
    if existing is not None:
        _job_pools.pop(connection_string, None)
    pool = await asyncpg.create_pool(connection_string)
    _job_pools[connection_string] = pool
    return pool
