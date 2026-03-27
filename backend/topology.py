from __future__ import annotations

from uuid import UUID

import asyncpg

from backend.ghost_mcp import ghost_list_databases
from db import models


def _ghost_meta_for_id(databases: list, ghost_id: str) -> dict | None:
    for d in databases:
        if d.get("id") == ghost_id:
            return d
    return None


async def build_topology_response(pool: asyncpg.Pool) -> models.TopologyResponse:
    listing = await ghost_list_databases()
    raw_dbs = listing.get("databases") or []
    databases: list = raw_dbs if isinstance(raw_dbs, list) else []

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT job_id, query, status, ghost_db_id, parent_job_id, created_at
            FROM jobs
            WHERE ghost_db_id IS NOT NULL
            ORDER BY created_at NULLS LAST
            """
        )

    job_by_ghost: dict[str, asyncpg.Record] = {r["ghost_db_id"]: r for r in rows}
    nodes_by_job_id: dict[UUID, models.TopologyNode] = {}

    for r in rows:
        gid = r["ghost_db_id"]
        meta = _ghost_meta_for_id(databases, gid)
        nodes_by_job_id[r["job_id"]] = models.TopologyNode(
            ghost_id=gid,
            name=(meta or {}).get("name") or f"job-{str(r['job_id'])[:8]}",
            ghost_status=(meta or {}).get("status") or "unknown",
            size=(meta or {}).get("size"),
            job_id=r["job_id"],
            query=r["query"],
            job_status=r["status"],
            parent_job_id=r["parent_job_id"],
            created_at=r["created_at"],
            children=[],
        )

    top_level: list[models.TopologyNode] = []
    for node in nodes_by_job_id.values():
        pid = node.parent_job_id
        if pid is None:
            top_level.append(node)
            continue
        parent = nodes_by_job_id.get(pid)
        if parent is not None:
            parent.children.append(node)
        else:
            top_level.append(node)

    def sort_key(n: models.TopologyNode):
        return n.created_at.isoformat() if n.created_at else ""

    top_level.sort(key=sort_key)
    for n in nodes_by_job_id.values():
        n.children.sort(key=sort_key)

    orphan_ghosts: list[models.TopologyNode] = []
    linked_ids = set(job_by_ghost.keys())
    for d in databases:
        gid = d.get("id")
        if not gid or gid in linked_ids:
            continue
        orphan_ghosts.append(
            models.TopologyNode(
                ghost_id=gid,
                name=d.get("name") or gid[:8],
                ghost_status=d.get("status") or "unknown",
                size=d.get("size"),
                job_id=None,
                query=None,
                job_status=None,
                parent_job_id=None,
                created_at=None,
                children=[],
            )
        )
    orphan_ghosts.sort(key=lambda n: n.name)

    root = models.TopologyNode(
        ghost_id="master",
        name="Master registry",
        ghost_status="registry",
        size=None,
        job_id=None,
        query=None,
        job_status=None,
        parent_job_id=None,
        created_at=None,
        children=[*top_level, *orphan_ghosts],
    )

    return models.TopologyResponse(root=root)
