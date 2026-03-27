import os
import httpx
from google import genai
from typing import Dict, Optional
from bs4 import BeautifulSoup

async def enrich_lead(lead: Dict) -> Dict:
    """
    Enriches a lead with Claude by:
    1. Scraping their website (if available)
    2. Generating a research summary with business signals
    3. Attempting to extract email from website
    
    Args:
        lead: Dict with name, phone, address, website, rating
    
    Returns:
        Lead dict with added research_summary and possibly email
    """
    website = lead.get("website")
    
    if not website:
        lead["research_summary"] = f"Business: {lead.get('name')}. No website available. Rating: {lead.get('rating', 'N/A')}/5"
        return lead
    
    # Scrape website content
    website_text = await scrape_website(website)
    
    # Use Gemini Flash to analyze and summarize
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not set")
    
    client = genai.Client(api_key=gemini_api_key)
    
    prompt = f"""Analyze this business website and provide a concise research summary (2-3 sentences max).

Business Name: {lead.get('name')}
Website: {website}
Rating: {lead.get('rating', 'N/A')}/5
Location: {lead.get('address')}

Website Content:
{website_text[:4000]}

Focus on:
- What services they offer
- Business signals (size, professionalism, tech-savviness)
- Pain points or opportunities for our SaaS pitch

Keep it brief and actionable."""

    response = client.models.generate_content(
        model='gemini-3-flash-preview',
        contents=prompt
    )
    research_summary = response.text
    lead["research_summary"] = research_summary
    
    # Try to extract email from website text
    email = extract_email_from_text(website_text)
    if email:
        lead["email"] = email
    
    return lead


async def scrape_website(url: str) -> str:
    """
    Scrapes website and returns clean text content.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:8000]  # Limit to 8k chars
            
    except Exception as e:
        return f"[Website scraping failed: {str(e)}]"


def extract_email_from_text(text: str) -> Optional[str]:
    """
    Simple regex-based email extraction from text.
    """
    import re
    
    # Look for email patterns
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text)
    
    if matches:
        # Filter out common noise emails
        noise = ['example.com', 'domain.com', 'email.com', 'test.com']
        for email in matches:
            if not any(n in email.lower() for n in noise):
                return email
    
    return None
