-- Run against the master Ghost DB if you already created `jobs` without error_detail:
--   ghost sql <master-db-id> < db/migrations/001_add_jobs_error_detail.sql

ALTER TABLE jobs ADD COLUMN IF NOT EXISTS error_detail TEXT;
