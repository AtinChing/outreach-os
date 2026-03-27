from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


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


class JobCreateRequest(BaseModel):
    query: str


class JobStatusResponse(BaseModel):
    job_id: UUID
    query: str
    status: str
    created_at: Optional[datetime] = None


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
