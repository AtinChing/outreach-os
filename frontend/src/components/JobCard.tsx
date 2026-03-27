interface JobCardProps {
  job_id: string;
  query: string;
  status: string;
  created_at: string;
}

export default function JobCard({ job_id, query, status, created_at }: JobCardProps) {
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
    </div>
  );
}
