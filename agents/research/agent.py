from agents.research import search, enrich, writer

async def main(job_id: str, connection_string: str):
    # TODO: pass connection_string through to writer.py
    leads = await search.find_leads(query="")
    enriched = [await enrich.enrich_lead(lead) for lead in leads]
    await writer.save_leads(job_id, enriched, connection_string)
