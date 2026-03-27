# Quick Start - Research Agent

Get the Research Agent running in 2 minutes!

## Step 1: Add Your API Keys to .env

```bash
# Copy example
cp .env.example .env

# Edit .env and add:
HASDATA_API_KEY=your-hasdata-key
GEMINI_API_KEY=your-gemini-key
MASTER_DATABASE_URL=postgresql://ghost:ghostpass@localhost:5432/master_db
```

## Step 2: Start Local Database

```bash
docker-compose up postgres -d
```

Wait 5 seconds for database to initialize.

## Step 3: Run Research Agent

```bash
cd agents/research
pip install -r requirements.txt
python example.py
```

## Expected Output

```
🚀 Starting Research Agent
   Job ID: 123e4567-e89b-12d3-a456-426614174000
   Query: coffee shops in Seattle WA
   Lead Count: 5

🔍 Research Agent started for job 123e4567-e89b-12d3-a456-426614174000
📝 Query: coffee shops in Seattle WA

🌍 Searching for 5 leads...
✅ Found 5 leads (2.1 seconds)

🧠 Enriching leads with Gemini...
  [1/5] Enriching Starbucks Reserve...
  [2/5] Enriching Victrola Coffee...
  [3/5] Enriching Espresso Vivace...
  [4/5] Enriching Caffe Vita...
  [5/5] Enriching Elm Coffee...
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
```

## View Your Leads

```bash
# Connect to database
docker exec -it research-to-outreach-postgres-1 psql -U ghost -d master_db

# Query leads
SELECT name, phone, website, research_summary FROM leads LIMIT 5;
```

## That's It!

You now have a working Research Agent that finds and enriches leads in ~2-3 seconds! 🎉

## Troubleshooting

**"HASDATA_API_KEY not set"**
→ Make sure you added it to `.env` in the project root

**"Connection refused"**
→ Run `docker-compose up postgres -d` first

**"GEMINI_API_KEY not set"**
→ Get free key from https://aistudio.google.com/app/apikey
