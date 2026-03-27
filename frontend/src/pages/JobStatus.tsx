import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useAuth0 } from "@auth0/auth0-react";
import { getJob, getLeads, Lead } from "../api/client";
import JobCard from "../components/JobCard";
import LeadsTable from "../components/LeadsTable";

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
  const [leads, setLeads] = useState<Lead[]>([]);
  const [error, setError] = useState<string | null>(null);

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
      } catch (err: any) {
        setError(err.message ?? "Failed to fetch job");
        clearInterval(intervalId);
      }
    }

    fetchJob();
    intervalId = setInterval(fetchJob, 3000);
    return () => clearInterval(intervalId);
  }, [job_id, getAccessTokenSilently]);

  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (!job) return <p>Loading...</p>;

  return (
    <div>
      <h1>Job Status</h1>
      <JobCard 
        job_id={job.job_id}
        query={job.query}
        status={job.status}
        created_at={job.created_at}
      />
      {job.status === "RESEARCH_COMPLETE" && (
        <>
          <h2>Leads</h2>
          <LeadsTable leads={leads} />
        </>
      )}
      {job.status === "FAILED" && (
        <p style={{ color: "red" }}>Job failed.</p>
      )}
    </div>
  );
}
