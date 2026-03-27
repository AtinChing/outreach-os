from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class Job(BaseModel):
    job_id: uuid.UUID
    query: str
    status: str
    db_connection_string: Optional[str] = None
    created_at: Optional[datetime] = None

class Lead(BaseModel):
    lead_id: uuid.UUID
    job_id: uuid.UUID
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    research_summary: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
