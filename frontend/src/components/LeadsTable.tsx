import type { Lead } from "../types";

interface LeadsTableProps {
  leads: Lead[];
}

export default function LeadsTable({ leads }: LeadsTableProps) {
  if (leads.length === 0) {
    return <p className="ibm-muted">No leads found.</p>;
  }

  return (
    <div className="ibm-table-wrap">
      <table className="ibm-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Phone</th>
            <th>Email</th>
            <th>Address</th>
            <th>Website</th>
            <th>Summary</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => (
            <tr key={lead.lead_id}>
              <td>{lead.name || "—"}</td>
              <td>{lead.phone || "—"}</td>
              <td>{lead.email || "—"}</td>
              <td>{lead.address || "—"}</td>
              <td>
                {lead.website ? (
                  <a href={lead.website} target="_blank" rel="noopener noreferrer">
                    Link
                  </a>
                ) : (
                  "—"
                )}
              </td>
              <td>{lead.research_summary || "—"}</td>
              <td>{lead.status || "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
