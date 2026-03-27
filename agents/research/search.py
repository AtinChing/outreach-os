import os
import httpx
from typing import List, Dict, Optional

async def find_leads(query: str, count: int = 10) -> List[Dict]:
    """
    Uses HasData's Google Maps Search API to find leads.
    
    Args:
        query: Natural language query like "plumbing leads in Austin TX"
        count: Number of leads to return
    
    Returns:
        List of lead dicts with: name, phone, address, website, rating
    """
    hasdata_api_key = os.getenv("HASDATA_API_KEY")
    if not hasdata_api_key:
        raise ValueError("HASDATA_API_KEY not set")
    
    # Parse query to extract business type and location
    # For MVP, assume format: "{business_type} in {location}"
    parts = query.lower().split(" in ")
    if len(parts) == 2:
        business_type = parts[0].strip()
        location = parts[1].strip()
        search_query = f"{business_type} {location}"
    else:
        search_query = query
    
    # Call HasData Google Maps Search API
    # Real-time response in ~2 seconds!
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            "https://api.hasdata.com/scrape/google-maps/search",
            params={
                "q": search_query,
            },
            headers={
                "x-api-key": hasdata_api_key,
                "Content-Type": "application/json",
            }
        )
        
        response.raise_for_status()
        data = response.json()
    
    # Check for errors
    if not data.get("success", True):
        error_msg = data.get("error", data.get("message", "Unknown error"))
        raise ValueError(f"HasData API error: {error_msg}")
    
    results = data.get("localResults", data.get("places", data.get("results", [])))
    
    # Transform HasData results to our format
    leads = []
    for item in results[:count]:
        # Skip if permanently closed (only if field exists and is True)
        if item.get("permanently_closed") is True or item.get("temporarily_closed") is True:
            continue
        
        lead = {
            "name": item.get("title") or item.get("name"),
            "phone": item.get("phone"),
            "address": item.get("address"),
            "website": item.get("website"),
            "rating": item.get("rating") or item.get("total_score"),
            "email": None,  # Will be enriched later if possible
        }
        
        # Only add leads with at least a name
        if lead["name"]:
            leads.append(lead)
    
    return leads[:count]
