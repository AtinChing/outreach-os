import asyncio

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend import orchestrator
from backend.auth import verify_token
from backend.topology import build_topology_response
from db import models
from db.client import get_job_pool, get_master_pool

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

_JOB_SELECT = """
    SELECT job_id, query, status, created_at, error_detail,
           parent_job_id, ghost_db_id, provisioning_ms, research_completed_at
    FROM jobs
"""


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
    asyncio.create_task(orchestrator.trigger_research(str(job_id)))

    return {"job_id": job_id, "status": row["status"], "created_at": row["created_at"]}


@app.get("/jobs", response_model=list[models.JobStatusResponse])
async def list_jobs(token: dict = Depends(verify_token)):
    pool = await get_master_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(f"{_JOB_SELECT} ORDER BY created_at DESC NULLS LAST")
    return [models.JobStatusResponse(**dict(row)) for row in rows]


@app.get("/jobs/{job_id}", response_model=models.JobStatusResponse)
async def get_job(
    job_id: str,
    token: dict = Depends(verify_token),
):
    pool = await get_master_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"{_JOB_SELECT} WHERE job_id = $1",
            job_id,
        )

    if not row:
        raise HTTPException(status_code=404, detail="Job not found")

    return models.JobStatusResponse(**dict(row))


@app.post("/jobs/{job_id}/fork", response_model=models.ForkJobResponse)
async def fork_job(
    job_id: str,
    token: dict = Depends(verify_token),
):
    pool = await get_master_pool()
    async with pool.acquire() as conn:
        parent = await conn.fetchrow(
            "SELECT job_id, query, ghost_db_id, status FROM jobs WHERE job_id = $1",
            job_id,
        )

        if not parent:
            raise HTTPException(status_code=404, detail="Job not found")

        if not parent["ghost_db_id"]:
            raise HTTPException(
                status_code=400,
                detail="This job has no Ghost database id (created before fork support). Run db/migrations/002_ghost_fork_topology.sql and create a new job.",
            )

        if parent["status"] != "RESEARCH_COMPLETE":
            raise HTTPException(
                status_code=400,
                detail="Fork is only available after research completes on the parent job.",
            )

        row = await conn.fetchrow(
            """
            INSERT INTO jobs (query, status, parent_job_id)
            VALUES ($1, 'FORKED', $2)
            RETURNING job_id, status, created_at
            """,
            parent["query"],
            parent["job_id"],
        )

    new_job_id = str(row["job_id"])

    try:
        connection_string, ghost_id, provisioning_ms = await orchestrator.fork_job_database(
            parent_job_id=job_id,
            new_job_id=new_job_id,
            parent_query=parent["query"],
            parent_ghost_db_id=parent["ghost_db_id"],
        )
    except Exception as exc:
        pool = await get_master_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE jobs SET status = 'FAILED', error_detail = $2 WHERE job_id = $1",
                new_job_id,
                str(exc),
            )
        raise HTTPException(status_code=502, detail=f"Ghost fork failed: {exc}") from exc

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
            ghost_id,
            provisioning_ms,
            new_job_id,
        )

    asyncio.create_task(
        orchestrator.trigger_research_on_forked_db(new_job_id, connection_string)
    )

    return models.ForkJobResponse(
        job_id=row["job_id"],
        parent_job_id=parent["job_id"],
        status=row["status"],
        created_at=row["created_at"],
    )


@app.get("/topology", response_model=models.TopologyResponse)
async def get_topology(token: dict = Depends(verify_token)):
    pool = await get_master_pool()
    return await build_topology_response(pool)


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
