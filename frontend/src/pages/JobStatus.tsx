import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useAuth0 } from "@auth0/auth0-react";
import { getJob } from "../api/client";

const TERMINAL_STATUSES = ["RESEARCH_COMPLETE", "FAILED"];

type JobData = {
  job_id: string;
  query: string;
  status: string;
  created_at: string;
};

export default function JobStatus() {
  const { job_id } = useParams<{ job_id: string }>();
  const { getAccessTokenSilently } = useAuth0();
  const [job, setJob] = useState<JobData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval>;

    async function fetchJob() {
      try {
        const token = await getAccessTokenSilently();
        const data = await getJob(job_id!, token);
        setJob(data);
        if (TERMINAL_STATUSES.includes(data.status)) {
          clearInterval(intervalId);
        }
      } catch (err: any) {
        setError(err.message ?? "Failed to fetch job");
        clearInterval(intervalId);
      }
    }

    fetchJob();
    intervalId = setInterval(fetchJob, 3000);
    return () => clearInterval(intervalId);
  }, [job_id]);

  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (!job) return <p>Loading...</p>;

  return (
    <div>
      <h1>Job Status</h1>
      <p><strong>ID:</strong> {job.job_id}</p>
      <p><strong>Query:</strong> {job.query}</p>
      <p><strong>Status:</strong> {job.status}</p>
      <p><strong>Created:</strong> {new Date(job.created_at).toLocaleString()}</p>
      {job.status === "RESEARCH_COMPLETE" && (
        <p style={{ color: "green" }}>Research complete.</p>
      )}
      {job.status === "FAILED" && (
        <p style={{ color: "red" }}>Job failed.</p>
      )}
    </div>
  );
}
