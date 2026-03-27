"""
Call Ghost's MCP server tools (ghost_create, ghost_fork, ghost_list, …) from the backend.

Ghost CLI exposes these as MCP tool names (see `ghost mcp list`). This replaces shelling out
to `ghost create` / `ghost connect` / `ghost sql`.
"""

from __future__ import annotations

import json
import os
import asyncio
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Serialize MCP stdio usage — concurrent calls would corrupt one session.
_ghost_stdio_lock: asyncio.Lock | None = None


def _lock() -> asyncio.Lock:
    global _ghost_stdio_lock
    if _ghost_stdio_lock is None:
        _ghost_stdio_lock = asyncio.Lock()
    return _ghost_stdio_lock


def _ghost_command() -> str:
    return os.environ.get("GHOST_MCP_COMMAND", "ghost")


def _ghost_stdio_args() -> list[str]:
    raw = os.environ.get("GHOST_MCP_STDIO_ARGS", "mcp,start,stdio")
    return [p.strip() for p in raw.split(",") if p.strip()]


def _parse_tool_result(result) -> dict[str, Any]:
    sc = getattr(result, "structuredContent", None)
    if isinstance(sc, dict):
        return sc
    for block in result.content or []:
        text = getattr(block, "text", None) or ""
        text = text.strip()
        if not text:
            continue
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    raise RuntimeError("Ghost MCP tool returned no parseable JSON object")


async def call_ghost_tool(name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    """Invoke a Ghost MCP tool by name (e.g. ghost_create, ghost_fork, ghost_list)."""
    params = StdioServerParameters(command=_ghost_command(), args=_ghost_stdio_args())
    async with _lock():
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments or {})
                if result.isError:
                    msg = _format_error_payload(result)
                    raise RuntimeError(f"Ghost MCP {name} failed: {msg}")
                return _parse_tool_result(result)


def _format_error_payload(result) -> str:
    parts: list[str] = []
    for block in result.content or []:
        t = getattr(block, "text", None)
        if t:
            parts.append(t)
    return "; ".join(parts) if parts else "unknown error"


async def ghost_create_database(*, name: str, wait: bool = True) -> dict[str, Any]:
    return await call_ghost_tool("ghost_create", {"name": name, "wait": wait})


async def ghost_fork_database(*, source_id: str, name: str | None = None, wait: bool = True) -> dict[str, Any]:
    args: dict[str, Any] = {"id": source_id, "wait": wait}
    if name is not None:
        args["name"] = name
    return await call_ghost_tool("ghost_fork", args)


async def ghost_list_databases() -> dict[str, Any]:
    return await call_ghost_tool("ghost_list", {})
