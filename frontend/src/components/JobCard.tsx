interface JobCardProps {
  job_id: string;
  query: string;
  status: string;
  created_at: string;
  provisioning_ms?: number | null;
  research_completed_at?: string | null;
}

function formatElapsedMs(createdAt: string, completedAt: string): string {
  const a = new Date(createdAt).getTime();
  const b = new Date(completedAt).getTime();
  if (Number.isNaN(a) || Number.isNaN(b) || b < a) return "—";
  const ms = b - a;
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

export default function JobCard({
  job_id,
  query,
  status,
  created_at,
  provisioning_ms,
  research_completed_at,
}: JobCardProps) {
  const when = new Date(created_at).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });

  return (
    <div className="ibm-panel" style={{ marginBottom: "1.5rem" }}>
      <p className="ibm-panel__label">Job record</p>
      <p className="ibm-detail__block-label">Brief</p>
      <p className="ibm-detail__query-body" style={{ marginBottom: "1rem" }}>
        {query}
      </p>
      <p className="ibm-detail__block-label">Job ID</p>
      <p className="ibm-detail__mono">{job_id}</p>
      <p className="ibm-detail__block-label">Status</p>
      <p className="ibm-detail__mono">{status.replace(/_/g, " ")}</p>
      <p className="ibm-detail__block-label">Submitted</p>
      <p className="ibm-detail__mono">{when}</p>
      {provisioning_ms != null && provisioning_ms >= 0 && (
        <>
          <p className="ibm-detail__block-label">Ghost provision</p>
          <p className="ibm-detail__mono">Ghost DB provisioned in {provisioning_ms}ms.</p>
        </>
      )}
      {status === "RESEARCH_COMPLETE" && research_completed_at && (
        <>
          <p className="ibm-detail__block-label">Submission → research complete</p>
          <p className="ibm-detail__mono">{formatElapsedMs(created_at, research_completed_at)}</p>
        </>
      )}
    </div>
  );
}
