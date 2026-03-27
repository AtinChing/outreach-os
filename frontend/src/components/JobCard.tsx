interface JobCardProps {
  job_id: string;
  query: string;
  status: string;
  created_at: string;
}

export default function JobCard({ job_id, query, status, created_at }: JobCardProps) {
  return (
    <div style={{ border: "1px solid #ccc", padding: "16px", borderRadius: "8px", marginBottom: "20px" }}>
      <h2>Job Details</h2>
      <p><strong>ID:</strong> {job_id}</p>
      <p><strong>Query:</strong> {query}</p>
      <p><strong>Status:</strong> {status}</p>
      <p><strong>Created:</strong> {new Date(created_at).toLocaleString()}</p>
    </div>
  );
}
