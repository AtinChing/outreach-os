#!/usr/bin/env python3
"""
Entrypoint for Research Agent when deployed on TrueFoundry.

Expects environment variables:
- JOB_ID: UUID of the job
- QUERY: Natural language search query
- JOB_CONNECTION_STRING: PostgreSQL connection string for job DB
- LEAD_COUNT: (optional) Number of leads to find, default 10
"""

import asyncio
import os
import sys


def cli_main() -> None:
    try:
        from .agent import main as run_research
    except ImportError:
        from agent import main as run_research

    job_id = os.getenv("JOB_ID")
    query = os.getenv("QUERY")
    job_connection_string = os.getenv("JOB_CONNECTION_STRING")
    _lead_count = int(os.getenv("LEAD_COUNT", "10"))

    if not job_id:
        print("❌ Error: JOB_ID environment variable not set")
        sys.exit(1)

    if not query:
        print("❌ Error: QUERY environment variable not set")
        sys.exit(1)

    if not job_connection_string:
        print("❌ Error: JOB_CONNECTION_STRING environment variable not set")
        sys.exit(1)

    try:
        asyncio.run(run_research(job_id, job_connection_string))
        print("\n✅ Research Agent completed successfully")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Research Agent failed: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
