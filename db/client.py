import os
import asyncpg
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# Module-level pool cache
_master_pool: asyncpg.Pool | None = None
_job_pools: dict[str, asyncpg.Pool] = {}


async def get_master_pool() -> asyncpg.Pool:
    global _master_pool
    if _master_pool is None:
        url = os.getenv("MASTER_DATABASE_URL")
        _master_pool = await asyncpg.create_pool(url)
    return _master_pool


async def get_job_pool(connection_string: str) -> asyncpg.Pool:
    if connection_string not in _job_pools:
        _job_pools[connection_string] = await asyncpg.create_pool(connection_string)
    return _job_pools[connection_string]
