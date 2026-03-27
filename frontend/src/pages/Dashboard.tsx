import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth0 } from "@auth0/auth0-react";
import { listJobs, submitJob } from "../api/client";
import type { JobSummary } from "../types";

function getStageInfo(status: string): { title: string; description: string } {
  switch (status) {
    case "INITIATED":
      return {
        title: "Pipeline active",
        description:
          "Workspace provisioning, map search, and lead enrichment are running. Status updates automatically.",
      };
    case "RESEARCH_COMPLETE":
      return {
        title: "Research complete",
        description: "All leads have been written to the job database. Open the workspace to review the table.",
      };
    case "FAILED":
      return {
        title: "Job failed",
        description:
          "The pipeline exited with an error. Use Show error logs for the captured traceback and subprocess output, or check the API server terminal.",
      };
    case "FORKED":
      return {
        title: "Fork created",
        description: "Ghost is copying the parent database; research will start on the fork shortly.",
      };
    default:
      return {
        title: status,
        description: "Tracking this job state.",
      };
  }
}

function statusTagClass(status: string): string {
  if (status === "RESEARCH_COMPLETE") return "ibm-tag ibm-tag--done";
  if (status === "FAILED") return "ibm-tag ibm-tag--fail";
  if (status === "FORKED") return "ibm-tag ibm-tag--active";
  return "ibm-tag ibm-tag--active";
}

function formatSubmittedAt(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function Dashboard() {
  const { isAuthenticated, loginWithRedirect, logout, getAccessTokenSilently, user } = useAuth0();
  const [query, setQuery] = useState("");
  const [jobs, setJobs] = useState<JobSummary[]>([]);
  const [listLoading, setListLoading] = useState(true);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [showErrorLogs, setShowErrorLogs] = useState(false);

  const refreshJobs = useCallback(async () => {
    const token = await getAccessTokenSilently();
    const list = await listJobs(token);
    setJobs(list);
  }, [getAccessTokenSilently]);

  useEffect(() => {
    if (!isAuthenticated) return;

    let cancelled = false;
    let intervalId: ReturnType<typeof setInterval>;

    async function load() {
      try {
        await refreshJobs();
      } catch (err: unknown) {
        if (!cancelled) {
          const msg = err instanceof Error ? err.message : "Failed to load jobs";
          setError(msg);
        }
      } finally {
        if (!cancelled) setListLoading(false);
      }
    }

    load();
    intervalId = setInterval(load, 3000);
    return () => {
      cancelled = true;
      clearInterval(intervalId);
    };
  }, [isAuthenticated, refreshJobs]);

  useEffect(() => {
    setShowErrorLogs(false);
  }, [selectedJobId]);

  const selectedJob = useMemo(
    () => jobs.find((j) => j.job_id === selectedJobId) ?? null,
    [jobs, selectedJobId]
  );

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitLoading(true);
    setError(null);
    const submittedQuery = query.trim();
    try {
      const token = await getAccessTokenSilently();
      const job = await submitJob(submittedQuery, token);
      const newSummary: JobSummary = {
        job_id: job.job_id,
        query: submittedQuery,
        status: job.status,
        created_at: job.created_at ?? null,
      };
      setJobs((prev) => [newSummary, ...prev.filter((j) => j.job_id !== newSummary.job_id)]);
      setSelectedJobId(newSummary.job_id);
      setQuery("");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setSubmitLoading(false);
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="ibm-shell">
        <div className="ibm-login-panel">
          <p className="ibm-wordmark" style={{ marginBottom: "0.5rem" }}>
            Outreach OS
          </p>
          <h1 className="ibm-title" style={{ fontSize: "1.25rem", marginBottom: "1rem" }}>
            Sign in to run research jobs
          </h1>
          <p className="ibm-muted" style={{ marginBottom: "1.5rem" }}>
            Authenticated sessions only. Your jobs and lead data stay tied to your workspace.
          </p>
          <button type="button" className="ibm-btn" onClick={() => loginWithRedirect()}>
            Log in
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="ibm-shell">
      <header className="ibm-header">
        <div>
          <p className="ibm-wordmark">Outreach OS · Research console</p>
          <h1 className="ibm-title">Lead research</h1>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
          <Link className="ibm-btn ibm-btn--ghost" to="/topology" style={{ textDecoration: "none" }}>
            Ghost topology
          </Link>
          {user?.email && (
            <span className="ibm-muted" style={{ fontSize: "0.75rem" }}>
              {user.email}
            </span>
          )}
          <button
            type="button"
            className="ibm-btn ibm-btn--ghost"
            onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
          >
            Log out
          </button>
        </div>
      </header>

      <section className="ibm-panel">
        <p className="ibm-panel__label">New run</p>
        <h2 className="ibm-hero-title">Turn a plain-language brief into enriched leads.</h2>
        <p className="ibm-hero-copy">
          Describe who you want to find. We provision an isolated database per job, search maps, enrich with AI,
          and surface results here as soon as the pipeline advances.
        </p>
        <form onSubmit={handleSubmit} className="ibm-form-row">
          <input
            className="ibm-input"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. Independent coffee roasters in Portland, OR"
            required
            aria-label="Research query"
          />
          <button type="submit" className="ibm-btn" disabled={submitLoading}>
            {submitLoading ? "Submitting…" : "Submit job"}
          </button>
        </form>
        {error && <p className="ibm-error">{error}</p>}
      </section>

      <section>
        <h2 className="ibm-section-title">Jobs</h2>
        {listLoading && jobs.length === 0 ? (
          <p className="ibm-muted">Loading jobs…</p>
        ) : jobs.length === 0 ? (
          <p className="ibm-muted">No jobs yet. Submit a query above to create your first run.</p>
        ) : (
          <div className="ibm-job-grid">
            {jobs.map((job) => (
              <button
                key={job.job_id}
                type="button"
                className={`ibm-job-card${selectedJobId === job.job_id ? " ibm-job-card--selected" : ""}`}
                onClick={() => setSelectedJobId(job.job_id)}
              >
                <p className="ibm-job-card__query">{job.query}</p>
                <div className="ibm-job-card__meta">
                  <span className={statusTagClass(job.status)}>{job.status.replace(/_/g, " ")}</span>
                  <span>{job.job_id.slice(0, 8)}</span>
                </div>
              </button>
            ))}
          </div>
        )}

        {selectedJob && (
          <div className="ibm-detail">
            <div className="ibm-detail__col ibm-detail__col--left">
              <p className="ibm-detail__block-label">Current stage</p>
              <h3 className="ibm-detail__stage-title">{getStageInfo(selectedJob.status).title}</h3>
              <p className="ibm-detail__stage-desc">{getStageInfo(selectedJob.status).description}</p>
              {selectedJob.status === "FAILED" && (
                <>
                  <button
                    type="button"
                    className="ibm-btn ibm-btn--danger"
                    onClick={() => setShowErrorLogs((v) => !v)}
                    aria-expanded={showErrorLogs}
                  >
                    {showErrorLogs ? "Hide error logs" : "Show error logs"}
                  </button>
                  {showErrorLogs && (
                    <pre className="ibm-error-logs">
                      {selectedJob.error_detail?.trim() ||
                        "No error details were stored for this job. If the database was migrated after the failure, re-run the job; otherwise check the API server terminal."}
                    </pre>
                  )}
                </>
              )}
            </div>
            <div className="ibm-detail__col">
              <p className="ibm-detail__block-label">Brief</p>
              <p className="ibm-detail__query-body">{selectedJob.query}</p>
              <p className="ibm-detail__block-label">Submitted</p>
              <p className="ibm-detail__mono">{formatSubmittedAt(selectedJob.created_at)}</p>
              <p className="ibm-detail__block-label">Job ID</p>
              <p className="ibm-detail__mono">{selectedJob.job_id}</p>
              {selectedJob.status === "RESEARCH_COMPLETE" && (
                <Link className="ibm-detail__link" to={`/jobs/${selectedJob.job_id}`}>
                  Open leads workspace →
                </Link>
              )}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
