import { Lead } from "../api/client";

interface LeadsTableProps {
  leads: Lead[];
}

export default function LeadsTable({ leads }: LeadsTableProps) {
  if (leads.length === 0) {
    return <p>No leads found.</p>;
  }

  return (
    <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "20px" }}>
      <thead>
        <tr style={{ borderBottom: "2px solid #ccc" }}>
          <th style={{ padding: "8px", textAlign: "left" }}>Name</th>
          <th style={{ padding: "8px", textAlign: "left" }}>Phone</th>
          <th style={{ padding: "8px", textAlign: "left" }}>Email</th>
          <th style={{ padding: "8px", textAlign: "left" }}>Address</th>
          <th style={{ padding: "8px", textAlign: "left" }}>Website</th>
          <th style={{ padding: "8px", textAlign: "left" }}>Summary</th>
          <th style={{ padding: "8px", textAlign: "left" }}>Status</th>
        </tr>
      </thead>
      <tbody>
        {leads.map((lead) => (
          <tr key={lead.lead_id} style={{ borderBottom: "1px solid #eee" }}>
            <td style={{ padding: "8px" }}>{lead.name || "—"}</td>
            <td style={{ padding: "8px" }}>{lead.phone || "—"}</td>
            <td style={{ padding: "8px" }}>{lead.email || "—"}</td>
            <td style={{ padding: "8px" }}>{lead.address || "—"}</td>
            <td style={{ padding: "8px" }}>
              {lead.website ? (
                <a href={lead.website} target="_blank" rel="noopener noreferrer">
                  Link
                </a>
              ) : (
                "—"
              )}
            </td>
            <td style={{ padding: "8px" }}>{lead.research_summary || "—"}</td>
            <td style={{ padding: "8px" }}>{lead.status || "—"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
