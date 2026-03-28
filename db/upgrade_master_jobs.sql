-- Idempotent patches for master DB `jobs` table (safe to re-run).
-- Use when GET /jobs fails with: column "error_detail" does not exist
-- (or similar) — your DB was created before these columns existed.
--
--   psql "$MASTER_DATABASE_URL" -f db/upgrade_master_jobs.sql

ALTER TABLE jobs ADD COLUMN IF NOT EXISTS error_detail TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS parent_job_id UUID REFERENCES jobs(job_id);
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS ghost_db_id TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS provisioning_ms INTEGER;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS research_completed_at TIMESTAMP;
