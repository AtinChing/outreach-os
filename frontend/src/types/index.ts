export interface JobSummary {
  job_id: string;
  query: string;
  status: string;
  created_at: string | null;
  error_detail?: string | null;
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
