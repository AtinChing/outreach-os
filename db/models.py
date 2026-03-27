from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Job(BaseModel):
    job_id: UUID
    query: str
    status: str
    db_connection_string: Optional[str] = None
    created_at: Optional[datetime] = None


class Lead(BaseModel):
    lead_id: UUID
    job_id: UUID
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    research_summary: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None


class ForkJobResponse(BaseModel):
    job_id: UUID
    parent_job_id: UUID
    status: str
    created_at: Optional[datetime] = None


class JobCreateRequest(BaseModel):
    query: str


class JobStatusResponse(BaseModel):
    job_id: UUID
    query: str
    status: str
    created_at: Optional[datetime] = None
    error_detail: Optional[str] = None
    parent_job_id: Optional[UUID] = None
    ghost_db_id: Optional[str] = None
    provisioning_ms: Optional[int] = None
    research_completed_at: Optional[datetime] = None


class TopologyNode(BaseModel):
    """One Ghost database in the topology tree (master registry is synthetic root)."""

    ghost_id: str
    name: str
    ghost_status: str
    size: Optional[str] = None
    job_id: Optional[UUID] = None
    query: Optional[str] = None
    job_status: Optional[str] = None
    parent_job_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    children: list["TopologyNode"] = Field(default_factory=list)


class TopologyResponse(BaseModel):
    root: TopologyNode


TopologyNode.model_rebuild()


class LeadsResponse(BaseModel):
    lead_id: UUID
    job_id: UUID
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    research_summary: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
