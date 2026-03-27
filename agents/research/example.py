#!/usr/bin/env python3
"""
Simple example of using the Research Agent.

This demonstrates the minimal code needed to run the agent.
"""

import asyncio
import uuid
import os
from dotenv import load_dotenv
from agent import run_research_agent

# Load environment variables from project root
load_dotenv(dotenv_path="../../.env")

async def example_usage():
    """
    Example: Find 5 coffee shop leads in Seattle.
    """
    
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    
    # Define your search query
    query = "coffee shops in Seattle WA"
    
    # For this example, we'll use the master DB as the job DB
    # In production, each job gets its own Ghost DB
    job_connection_string = os.getenv("MASTER_DATABASE_URL")
    
    # Number of leads to find
    lead_count = 5
    
    print(f"🚀 Starting Research Agent")
    print(f"   Job ID: {job_id}")
    print(f"   Query: {query}")
    print(f"   Lead Count: {lead_count}\n")
    
    try:
        # Run the research agent
        result = await run_research_agent(
            job_id=job_id,
            query=query,
            job_connection_string=job_connection_string,
            lead_count=lead_count
        )
        
        print(f"\n✅ Success!")
        print(f"   Status: {result['status']}")
        print(f"   Leads Found: {result['leads_count']}")
        print(f"   Job ID: {result['job_id']}")
        
        # Now you can query the database to see the leads
        print(f"\n💡 To view the leads, run:")
        print(f"   SELECT * FROM leads WHERE job_id = '{job_id}';")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


async def custom_query_example():
    """
    Example: Custom query with different parameters.
    """
    
    job_id = str(uuid.uuid4())
    
    # Try different queries:
    queries = [
        "plumbing companies in Austin TX",
        "dentists in Brooklyn NY",
        "yoga studios in Portland OR",
        "auto repair shops in Denver CO",
    ]
    
    # Pick one
    query = queries[0]
    
    job_connection_string = os.getenv("MASTER_DATABASE_URL")
    
    result = await run_research_agent(
        job_id=job_id,
        query=query,
        job_connection_string=job_connection_string,
        lead_count=10  # Find 10 leads
    )
    
    return result


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_usage())
    
    # Uncomment to try custom query:
    # asyncio.run(custom_query_example())
