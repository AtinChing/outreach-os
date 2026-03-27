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
# - GOOGLE_MAPS_API_KEY (from Google Cloud Console)
# - ANTHROPIC_API_KEY (from Anthropic Console)
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
   Lead Count: 5

🔍 Research Agent started for job 123e4567-e89b-12d3-a456-426614174000
📝 Query: coffee shops in Seattle WA

🌍 Searching for 5 leads...
✅ Found 5 leads

🧠 Enriching leads with Claude...
  [1/5] Enriching Starbucks Reserve Roastery...
  [2/5] Enriching Victrola Coffee Roasters...
  [3/5] Enriching Espresso Vivace...
  [4/5] Enriching Caffe Vita...
  [5/5] Enriching Elm Coffee Roasters...
✅ Enriched 5 leads

💾 Saving leads to Ghost DB...
✅ Saved 5 leads to job DB

📊 Updating job status...
✅ Updated job status to RESEARCH_COMPLETE

✅ Research Agent completed successfully!
📈 Summary: 5 leads researched and saved

✅ Success!
   Status: success
   Leads Found: 5
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

### "GOOGLE_MAPS_API_KEY not set"
→ Add your Google Maps API key to `.env`
→ Enable Places API in Google Cloud Console

### "ANTHROPIC_API_KEY not set"
→ Add your Anthropic API key to `.env`
→ Get key from https://console.anthropic.com

### "MASTER_DATABASE_URL not set"
→ Add your PostgreSQL connection string to `.env`
→ Format: `postgresql://user:pass@host:5432/dbname`

### "No leads found"
→ Try a more specific query
→ Check Google Maps API quota
→ Verify API key has correct permissions

## 📊 What You Get

For each lead, the agent provides:

- **Name**: Business name
- **Phone**: Contact phone number
- **Email**: Extracted from website (if available)
- **Address**: Full business address
- **Website**: Business website URL
- **Rating**: Google Maps rating (1-5 stars)
- **Research Summary**: 2-3 sentence AI-generated summary including:
  - Services offered
  - Business signals (size, professionalism)
  - Pain points for your pitch

## 💰 Cost Estimate

Per lead:
- Google Maps API: $0.017
- Claude API: $0.001
- **Total: ~$0.018 per lead**

Examples:
- 10 leads: ~$0.18
- 100 leads: ~$1.80
- 1,000 leads: ~$18.00

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
