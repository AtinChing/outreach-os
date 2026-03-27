export interface JobSummary {
  job_id: string;
  query: string;
  status: string;
  created_at: string | null;
  error_detail?: string | null;
  parent_job_id?: string | null;
  ghost_db_id?: string | null;
  provisioning_ms?: number | null;
  research_completed_at?: string | null;
}

export interface TopologyNode {
  ghost_id: string;
  name: string;
  ghost_status: string;
  size?: string | null;
  job_id?: string | null;
  query?: string | null;
  job_status?: string | null;
  parent_job_id?: string | null;
  created_at?: string | null;
  children: TopologyNode[];
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
