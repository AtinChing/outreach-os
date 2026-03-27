-- Per-job DB: a fresh Ghost DB created per query
-- Run this against each new per-job connection string

CREATE TABLE IF NOT EXISTS leads (
    lead_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL,
    name TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    website TEXT,
    research_summary TEXT,
    status TEXT DEFAULT 'RESEARCHED',
    created_at TIMESTAMP DEFAULT NOW()
);
