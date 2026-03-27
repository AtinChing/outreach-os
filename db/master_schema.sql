-- Master DB: one persistent Ghost DB that tracks all jobs
-- Run this once against MASTER_DATABASE_URL

CREATE TABLE jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'INITIATED',
    db_connection_string TEXT,
    error_detail TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- jobs.status flow: INITIATED → RESEARCH_COMPLETE
