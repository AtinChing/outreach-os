#!/usr/bin/env python3
"""
Entrypoint for Research Agent when deployed on TrueFoundry.

Expects environment variables:
- JOB_ID: UUID of the job
- QUERY: Natural language search query
- JOB_CONNECTION_STRING: PostgreSQL connection string for job DB
- LEAD_COUNT: (optional) Number of leads to find, default 10
"""

import os
import asyncio
import sys
from agent import run_research_agent

def main():
    # Read from environment
    job_id = os.getenv("JOB_ID")
    query = os.getenv("QUERY")
    job_connection_string = os.getenv("JOB_CONNECTION_STRING")
    lead_count = int(os.getenv("LEAD_COUNT", "10"))
    
    # Validate
    if not job_id:
        print("❌ Error: JOB_ID environment variable not set")
        sys.exit(1)
    
    if not query:
        print("❌ Error: QUERY environment variable not set")
        sys.exit(1)
    
    if not job_connection_string:
        print("❌ Error: JOB_CONNECTION_STRING environment variable not set")
        sys.exit(1)
    
    # Run agent
    try:
        result = asyncio.run(run_research_agent(
            job_id=job_id,
            query=query,
            job_connection_string=job_connection_string,
            lead_count=lead_count
        ))
        
        print(f"\n✅ Research Agent completed successfully")
        print(f"Result: {result}")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Research Agent failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
