import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth0 } from "@auth0/auth0-react";
import { forkJob, getTopology } from "../api/client";
import type { TopologyNode } from "../types";

function TopologyBranch({
  node,
  depth,
  onFork,
  forkBusyId,
}: {
  node: TopologyNode;
  depth: number;
  onFork: (jobId: string) => void;
  forkBusyId: string | null;
}) {
  const isMaster = node.ghost_id === "master";
  const pad = depth * 1.25;

  return (
    <li
      className="ibm-topology-node"
      style={{
        listStyle: "none",
        marginLeft: depth ? "1rem" : 0,
        paddingLeft: pad + "rem",
        borderLeft: depth ? "1px solid rgba(0,0,0,0.12)" : "none",
        marginBottom: "0.75rem",
      }}
    >
      <div
        className="ibm-panel"
        style={{
          marginBottom: 0,
          padding: "0.75rem 1rem",
          background: isMaster ? "rgba(15, 98, 254, 0.06)" : undefined,
        }}
      >
        <p className="ibm-panel__label" style={{ marginBottom: "0.25rem" }}>
          {isMaster ? "Registry root" : "Ghost database"}
        </p>
        <p className="ibm-detail__mono" style={{ marginBottom: "0.25rem", fontSize: "0.8125rem" }}>
          {node.name}
        </p>
        <p className="ibm-muted" style={{ fontSize: "0.75rem", marginBottom: "0.25rem" }}>
          Ghost ID: {node.ghost_id} · Status: {node.ghost_status}
          {node.size != null && node.size !== "" ? ` · ${node.size}` : ""}
        </p>
        {node.job_id && (
          <>
            <p className="ibm-muted" style={{ fontSize: "0.75rem", marginBottom: "0.25rem" }}>
              Job: {node.job_id.slice(0, 8)}… · Pipeline: {node.job_status?.replace(/_/g, " ") ?? "—"}
            </p>
            {node.query && (
              <p className="ibm-detail__query-body" style={{ fontSize: "0.8125rem", marginBottom: "0.5rem" }}>
                {node.query}
              </p>
            )}
            {node.job_status === "RESEARCH_COMPLETE" && (
              <button
                type="button"
                className="ibm-btn ibm-btn--ghost"
                style={{ marginTop: "0.25rem" }}
                disabled={forkBusyId === node.job_id}
                onClick={() => onFork(node.job_id!)}
              >
                {forkBusyId === node.job_id ? "Forking…" : "Fork database"}
              </button>
            )}
            <Link className="ibm-detail__link" style={{ marginLeft: "0.75rem" }} to={`/jobs/${node.job_id}`}>
              Open job →
            </Link>
          </>
        )}
      </div>
      {node.children?.length > 0 && (
        <ul style={{ marginTop: "0.5rem", paddingLeft: 0 }}>
          {node.children.map((ch) => (
            <TopologyBranch
              key={ch.ghost_id + (ch.job_id ?? "")}
              node={ch}
              depth={depth + 1}
              onFork={onFork}
              forkBusyId={forkBusyId}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

export default function GhostTopology() {
  const { isAuthenticated, loginWithRedirect, getAccessTokenSilently } = useAuth0();
  const navigate = useNavigate();
  const [root, setRoot] = useState<TopologyNode | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [forkBusyId, setForkBusyId] = useState<string | null>(null);

  const load = useCallback(async () => {
    const token = await getAccessTokenSilently();
    const data = await getTopology(token);
    setRoot(data.root);
  }, [getAccessTokenSilently]);

  useEffect(() => {
    if (!isAuthenticated) return;
    let cancelled = false;
    (async () => {
      try {
        await load();
      } catch (e: unknown) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to load topology");
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [isAuthenticated, load]);

  const onFork = async (jobId: string) => {
    setForkBusyId(jobId);
    setError(null);
    try {
      const token = await getAccessTokenSilently();
      const out = await forkJob(jobId, token);
      await load();
      navigate(`/jobs/${out.job_id}`);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Fork failed");
    } finally {
      setForkBusyId(null);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="ibm-shell">
        <p className="ibm-muted">Sign in to view Ghost topology.</p>
        <button type="button" className="ibm-btn" onClick={() => loginWithRedirect()}>
          Log in
        </button>
      </div>
    );
  }

  return (
    <div className="ibm-shell">
      <Link className="ibm-back" to="/">
        ← Research console
      </Link>
      <header className="ibm-header" style={{ marginBottom: "1.5rem" }}>
        <div>
          <p className="ibm-wordmark">Outreach OS · Ghost</p>
          <h1 className="ibm-title">Database topology</h1>
          <p className="ibm-hero-copy" style={{ marginTop: "0.75rem", maxWidth: "36rem" }}>
            Each job gets an isolated Postgres database provisioned through Ghost&apos;s MCP server. Forks branch from
            completed jobs so you can re-run research without touching the original snapshot.
          </p>
        </div>
      </header>

      {error && <p className="ibm-error">{error}</p>}

      {!root && !error && <p className="ibm-muted">Loading topology…</p>}

      {root && (
        <section className="ibm-panel">
          <p className="ibm-panel__label">Live Ghost databases</p>
          <p className="ibm-muted" style={{ fontSize: "0.8125rem", marginBottom: "1rem" }}>
            Data from <code className="ibm-detail__mono">ghost_list</code>, joined to jobs in the master registry. Child
            nodes are forks (same brief, new database).
          </p>
          <ul style={{ paddingLeft: 0, margin: 0 }}>
            <TopologyBranch node={root} depth={0} onFork={onFork} forkBusyId={forkBusyId} />
          </ul>
        </section>
      )}
    </div>
  );
}
