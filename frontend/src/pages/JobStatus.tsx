import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useAuth0 } from "@auth0/auth0-react";
import { getJob, getLeads } from "../api/client";
import type { Lead } from "../types";
import JobCard from "../components/JobCard";
import LeadsTable from "../components/LeadsTable";

const TERMINAL_STATUSES = ["RESEARCH_COMPLETE", "FAILED"];

type JobData = {
  job_id: string;
  query: string;
  status: string;
  created_at: string;
  error_detail?: string | null;
};

export default function JobStatus() {
  const { job_id } = useParams<{ job_id: string }>();
  const { getAccessTokenSilently } = useAuth0();
  const [job, setJob] = useState<JobData | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [showErrorLogs, setShowErrorLogs] = useState(false);

  useEffect(() => {
    setShowErrorLogs(false);
  }, [job_id]);

  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval>;

    async function fetchJob() {
      try {
        const token = await getAccessTokenSilently();
        const data = await getJob(job_id!, token);
        setJob(data);

        if (data.status === "RESEARCH_COMPLETE") {
          const leadsData = await getLeads(job_id!, token);
          setLeads(leadsData);
          clearInterval(intervalId);
        } else if (TERMINAL_STATUSES.includes(data.status)) {
          clearInterval(intervalId);
        }
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Failed to fetch job");
        clearInterval(intervalId);
      }
    }

    fetchJob();
    intervalId = setInterval(fetchJob, 3000);
    return () => clearInterval(intervalId);
  }, [job_id, getAccessTokenSilently]);

  if (error) {
    return (
      <div className="ibm-shell">
        <Link className="ibm-back" to="/">
          ← All jobs
        </Link>
        <p className="ibm-error">{error}</p>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="ibm-shell">
        <Link className="ibm-back" to="/">
          ← All jobs
        </Link>
        <p className="ibm-muted">Loading job…</p>
      </div>
    );
  }

  return (
    <div className="ibm-shell">
      <Link className="ibm-back" to="/">
        ← All jobs
      </Link>
      <header className="ibm-header" style={{ marginBottom: "1.5rem" }}>
        <div>
          <p className="ibm-wordmark">Outreach OS · Job workspace</p>
          <h1 className="ibm-title">Leads workspace</h1>
        </div>
      </header>

      <JobCard job_id={job.job_id} query={job.query} status={job.status} created_at={job.created_at} />

      {job.status === "FAILED" && (
        <div className="ibm-panel" style={{ marginBottom: "1.5rem" }}>
          <p className="ibm-panel__label">Diagnostics</p>
          <p className="ibm-muted" style={{ marginBottom: "0.75rem", fontSize: "0.8125rem" }}>
            Captured exception, traceback, and subprocess output (when applicable).
          </p>
          <button
            type="button"
            className="ibm-btn ibm-btn--danger"
            style={{ marginTop: 0 }}
            onClick={() => setShowErrorLogs((v) => !v)}
            aria-expanded={showErrorLogs}
          >
            {showErrorLogs ? "Hide error logs" : "Show error logs"}
          </button>
          {showErrorLogs && (
            <pre className="ibm-error-logs">
              {job.error_detail?.trim() ||
                "No error details were stored. Run db/migrations/001_add_jobs_error_detail.sql on the master DB if this column is missing, then re-run a job."}
            </pre>
          )}
        </div>
      )}

      {job.status === "RESEARCH_COMPLETE" && (
        <>
          <h2 className="ibm-section-title">Leads</h2>
          <LeadsTable leads={leads} />
        </>
      )}
    </div>
  );
}
