import asyncio
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.auth import verify_token
from db.client import get_master_pool, get_job_pool
from db import models
from backend import orchestrator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.post("/jobs")
async def create_job(
    body: models.JobCreateRequest,
    token: dict = Depends(verify_token),
):
    pool = await get_master_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO jobs (query) VALUES ($1) RETURNING job_id, status, created_at",
            body.query,
        )

    job_id = row["job_id"]
    asyncio.create_task(orchestrator.trigger_research(job_id))

    return {"job_id": job_id, "status": row["status"], "created_at": row["created_at"]}


@app.get("/jobs/{job_id}", response_model=models.JobStatusResponse)
async def get_job(
    job_id: str,
    token: dict = Depends(verify_token),
):
    pool = await get_master_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT job_id, query, status, created_at FROM jobs WHERE job_id = $1",
            job_id,
        )

    if not row:
        raise HTTPException(status_code=404, detail="Job not found")

    return models.JobStatusResponse(**dict(row))


@app.get("/jobs/{job_id}/leads", response_model=list[models.LeadsResponse])
async def get_leads(
    job_id: str,
    token: dict = Depends(verify_token),
):
    pool = await get_master_pool()
    async with pool.acquire() as conn:
        job_row = await conn.fetchrow(
            "SELECT db_connection_string FROM jobs WHERE job_id = $1",
            job_id,
        )

    if not job_row:
        raise HTTPException(status_code=404, detail="Job not found")

    connection_string = job_row["db_connection_string"]
    if not connection_string:
        return []

    job_pool = await get_job_pool(connection_string)
    async with job_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM leads WHERE job_id = $1",
            job_id,
        )

    return [models.LeadsResponse(**dict(row)) for row in rows]
