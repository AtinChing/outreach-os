import os
import httpx
from typing import List, Dict, Optional

async def find_leads(query: str, count: int = 10) -> List[Dict]:
    """
    Uses Google Maps Places API via Airbyte to find leads.
    
    Args:
        query: Natural language query like "plumbing leads in Austin TX"
        count: Number of leads to return
    
    Returns:
        List of lead dicts with: name, phone, address, website, rating
    """
    google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not google_maps_api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY not set")
    
    # Parse query to extract business type and location
    # For MVP, assume format: "{business_type} in {location}"
    parts = query.lower().split(" in ")
    if len(parts) == 2:
        business_type = parts[0].strip()
        location = parts[1].strip()
    else:
        business_type = query
        location = ""
    
    # Call Google Maps Places API (Text Search)
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            "https://maps.googleapis.com/maps/api/place/textsearch/json",
            params={
                "query": f"{business_type} {location}",
                "key": google_maps_api_key,
            }
        )
        response.raise_for_status()
        data = response.json()
    
    if data.get("status") != "OK":
        raise ValueError(f"Google Maps API error: {data.get('status')}")
    
    results = data.get("results", [])[:count]
    leads = []
    
    # Enrich each result with Place Details API
    async with httpx.AsyncClient(timeout=30.0) as client:
        for place in results:
            place_id = place.get("place_id")
            
            # Get detailed info
            detail_response = await client.get(
                "https://maps.googleapis.com/maps/api/place/details/json",
                params={
                    "place_id": place_id,
                    "fields": "name,formatted_phone_number,formatted_address,website,rating,business_status",
                    "key": google_maps_api_key,
                }
            )
            detail_response.raise_for_status()
            detail_data = detail_response.json()
            
            if detail_data.get("status") != "OK":
                continue
            
            result = detail_data.get("result", {})
            
            # Skip if business is closed
            if result.get("business_status") == "CLOSED_PERMANENTLY":
                continue
            
            lead = {
                "name": result.get("name"),
                "phone": result.get("formatted_phone_number"),
                "address": result.get("formatted_address"),
                "website": result.get("website"),
                "rating": result.get("rating"),
                "email": None,  # Will be enriched later if possible
            }
            
            leads.append(lead)
    
    return leads[:count]
