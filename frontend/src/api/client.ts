export const API_BASE = "http://localhost:8000";

export async function submitJob(
  query: string,
  token: string
): Promise<{ job_id: string; status: string; created_at: string }> {
  const res = await fetch(`${API_BASE}/jobs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) throw new Error(`submitJob failed: ${res.status}`);
  return res.json();
}

export async function getJob(
  jobId: string,
  token: string
): Promise<{ job_id: string; query: string; status: string; created_at: string }> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`getJob failed: ${res.status}`);
  return res.json();
}

export interface Lead {
  lead_id: string;
  job_id: string;
  name: string | null;
  phone: string | null;
  email: string | null;
  address: string | null;
  website: string | null;
  research_summary: string | null;
  status: string | null;
  created_at: string | null;
}

export async function getLeads(jobId: string, token: string): Promise<Lead[]> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/leads`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`getLeads failed: ${res.status}`);
  return res.json();
}
