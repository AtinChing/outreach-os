import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def get_master_pool():
    return await asyncpg.create_pool(dsn=os.getenv("MASTER_DATABASE_URL"))

async def get_job_pool(connection_string: str):
    return await asyncpg.create_pool(dsn=connection_string)
