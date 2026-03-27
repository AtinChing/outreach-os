# Get Started with Research Agent

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies
```bash
cd agents/research
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy .env.example to .env in project root
cp ../../.env.example ../../.env

# Edit .env and add your API keys:
# - MASTER_DATABASE_URL (PostgreSQL connection string)
# - HASDATA_API_KEY (from HasData)
# - OPENAI_API_KEY (from OpenAI Platform)
```

### 3. Run Example
```bash
python example.py
```

Expected output:
```
🚀 Starting Research Agent
   Job ID: 123e4567-e89b-12d3-a456-426614174000
   Query: coffee shops in Seattle WA
🔍 Research Agent started for job 123e4567-e89b-12d3-a456-426614174000
📝 Query: coffee shops in Seattle WA

🌍 Searching for 10 leads...
✅ Found 10 leads

🧠 Enriching leads with OpenAI...
  [1/10] Enriching Starbucks Reserve Roastery...
  [2/10] Enriching Victrola Coffee Roasters...
  ...
✅ Enriched 10 leads

💾 Saving leads to Ghost DB...
✅ Saved 10 leads to job DB

📊 Updating job status...
✅ Updated job status to RESEARCH_COMPLETE

✅ Research Agent completed successfully!
📈 Summary: 10 leads researched and saved

✅ Success!
   Status: success
   Leads Found: 10
   Job ID: 123e4567-e89b-12d3-a456-426614174000

💡 To view the leads, run:
   SELECT * FROM leads WHERE job_id = '123e4567-e89b-12d3-a456-426614174000';
```

## 📚 What to Read Next

### For Quick Setup
→ **QUICKSTART.md** - Detailed 5-minute setup guide

### For Understanding the System
→ **README.md** - Complete technical documentation
→ **ARCHITECTURE.md** - System design and data flow

### For Integration
→ **INTEGRATION.md** - How to integrate with Orchestrator
→ **example.py** - Simple usage examples

### For Deployment
→ **INTEGRATION.md** - TrueFoundry deployment guide
→ **Dockerfile.research** - Container configuration

### For Testing
→ **test_agent.py** - Run integration tests
→ **CHECKLIST.md** - Implementation checklist

## 🎯 Common Use Cases

### 1. Find Local Business Leads
```python
query = "plumbing companies in Austin TX"
lead_count = 10
```

### 2. Find Service Providers
```python
query = "dentists in Brooklyn NY"
lead_count = 20
```

### 3. Find Retail Locations
```python
query = "coffee shops in San Francisco CA"
lead_count = 15
```

### 4. Find Professional Services
```python
query = "law firms in Chicago IL"
lead_count = 25
```

## 🔧 Troubleshooting

### "HASDATA_API_KEY not set"
→ Add your HasData API key to `.env`
→ See HasData dashboard for key creation and quotas

### "OPENAI_API_KEY not set"
→ Add your OpenAI API key to `.env`
→ Get key from https://platform.openai.com

### "MASTER_DATABASE_URL not set"
→ Add your PostgreSQL connection string to `.env`
→ Format: `postgresql://user:pass@host:5432/dbname`

### "No leads found"
→ Try a more specific query
→ Check HasData API quota and response payload
→ Verify `HASDATA_API_KEY` is valid

## 📊 What You Get

For each lead, the agent provides:

- **Name**: Business name
- **Phone**: Contact phone number
- **Email**: Extracted from website (if available)
- **Address**: Full business address
- **Website**: Business website URL
- **Rating**: Maps-backed rating (1-5 stars) from search results
- **Research Summary**: 2-3 sentence AI-generated summary including:
  - Services offered
  - Business signals (size, professionalism)
  - Pain points for your pitch

## 💰 Cost Estimate

Per lead (approximate):
- HasData API: order of ~$0.002 (see HasData pricing)
- OpenAI API: ~$0.001
- **Total: varies with providers and volume**

Examples:
- 10 leads: small dollar amounts at typical HasData + OpenAI usage
- Scale: re-estimate from current provider pricing pages

## ⚡ Performance

- **Per lead**: 4-6 seconds
- **10 leads**: ~45 seconds
- **100 leads**: ~7.5 minutes

(Sequential processing. Can be optimized to ~15s for 10 leads with parallel enrichment)

## 🎓 Learning Path

1. **Start here** → Run `example.py`
2. **Understand** → Read `README.md`
3. **Test** → Run `test_agent.py`
4. **Customize** → Modify `example.py` with your queries
5. **Deploy** → Follow `INTEGRATION.md`

## 🆘 Need Help?

- **Setup issues**: See `QUICKSTART.md`
- **Integration questions**: See `INTEGRATION.md`
- **Architecture questions**: See `ARCHITECTURE.md`
- **Code questions**: See inline comments in source files

## ✅ Next Steps

After running the example:

1. ✅ View leads in database
2. ✅ Try different queries
3. ✅ Adjust lead count
4. ✅ Review research summaries
5. ✅ Integrate with your Orchestrator

## 🎉 You're Ready!

The Research Agent is fully functional and ready to discover and enrich leads for your outreach campaigns.

Happy lead hunting! 🎯
