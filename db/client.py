import os
import asyncpg
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


async def get_master_pool() -> asyncpg.Pool:
    url = os.getenv("MASTER_DATABASE_URL")
    return await asyncpg.create_pool(url)


async def get_job_pool(connection_string: str) -> asyncpg.Pool:
    return await asyncpg.create_pool(connection_string)
