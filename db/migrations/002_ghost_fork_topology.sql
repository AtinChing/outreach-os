-- Master DB: fork lineage, Ghost DB id for MCP fork/list, provisioning timing
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS parent_job_id UUID REFERENCES jobs(job_id);
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS ghost_db_id TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS provisioning_ms INTEGER;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS research_completed_at TIMESTAMP;
