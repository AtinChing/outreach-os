# Setting Up HasData for Lead Discovery

The Research Agent uses HasData's Google Maps Search API for ultra-fast lead discovery. Get results in ~2 seconds instead of 30-60 seconds!

## Why HasData?

### Speed Comparison

| Method | Response Time | Best For |
|--------|---------------|----------|
| **HasData** ⚡ | **~2 seconds** | **Real-time apps** |
| Apify | 30-60 seconds | Batch processing |
| Google Maps API | 5-10 seconds | Direct integration |

### Benefits
- ✅ **15-30x faster** than Apify
- ✅ **Real-time API** (no polling needed)
- ✅ **Super cheap** ($0.002 per lead)
- ✅ **Simple integration** (single API call)
- ✅ **FREE tier** (1,000 credits = 200 leads)

## Step 1: Create HasData Account

1. Go to **HasData**: https://hasdata.com/sign-up

2. Sign up (free account)

3. You'll get **1,000 free credits** automatically

## Step 2: Get Your API Key

1. Go to **Dashboard**: https://hasdata.com/dashboard

2. Click on **API Keys** or **Settings**

3. Copy your **API key** (starts with `hd_...` or similar)

## Step 3: Add to .env

Add your key to the `.env` file in the project root:

```bash
HASDATA_API_KEY=your-api-key-here
```

## Step 4: Test It

```bash
cd agents/research
python example.py
```

You should see:
```
🌍 Searching for 5 leads...
✅ Found 5 leads (in ~2 seconds!)

🧠 Enriching leads with Gemini...
  [1/5] Enriching Coffee Shop Name...
  ✅ Enriched 5 leads
```

## HasData Pricing

### Free Tier
- **1,000 credits FREE** (one-time)
- 200 leads FREE (5 credits per request)
- Perfect for testing!

### Paid Plans
- **Free**: $0/month (1,000 credits one-time)
- **Startup**: $49/month (60,000 credits)
- **Business**: $99/month (120,000 credits)
- **Enterprise**: $249/month (300,000 credits)

### Cost per Lead
- **5 credits per request** (one request = one lead search)
- **$0.42 per 1,000 requests** = **$0.0021 per lead**
- **10 leads**: ~$0.02
- **100 leads**: ~$0.21
- **1,000 leads**: ~$2.10

Extremely cheap! 💰

## What Data You Get

HasData's Google Maps Search API provides:
- ✅ Business name
- ✅ Phone number
- ✅ Address
- ✅ Website
- ✅ Rating (1-5 stars)
- ✅ Review count
- ✅ Business hours
- ✅ GPS coordinates
- ✅ Place ID

## How It Works

1. **Single API Call**: Send search query to HasData
2. **Real-time Response**: Get results in ~2 seconds
3. **Structured JSON**: Parse and use immediately
4. **No Polling**: No waiting, no complexity!

## Performance

- **Time**: ~2 seconds for 10 leads (15-30x faster than Apify!)
- **Cost**: $0.002 per lead (same as Apify)
- **Quality**: Same data as Google Maps API
- **Reliability**: 99.9% uptime

## Free Tier Limits

With 1,000 free credits:
- 200 leads FREE (5 credits per request)
- No rate limits
- No expiration

## API Example

```python
import httpx

async def search_leads(query: str, count: int = 10):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.hasdata.com/scrape/google/maps",
            params={
                "q": query,
                "limit": count,
            },
            headers={
                "x-api-key": "your-api-key",
            }
        )
        return response.json()

# Example usage
results = await search_leads("coffee shops in Seattle", 10)
```

## Troubleshooting

### "HASDATA_API_KEY not set"
→ Make sure you added the key to `.env` in the project root

### "API key not valid"
→ Check that you copied the entire key
→ Verify key is active in HasData dashboard

### "Insufficient credits"
→ Check your credit balance at https://hasdata.com/dashboard
→ Upgrade to a paid plan if needed

### "Rate limit exceeded"
→ HasData has generous rate limits
→ Contact support if you need higher limits

### Check Your Credits
→ Go to: https://hasdata.com/dashboard
→ See remaining credit balance

## Comparison: HasData vs Others

| Feature | HasData | Apify | Google Maps API |
|---------|---------|-------|-----------------|
| **Speed** | **2s** ⚡ | 30-60s | 5-10s |
| **Cost/lead** | **$0.002** | $0.002-0.005 | $0.017 |
| **Setup** | **Easy** | Moderate | Moderate |
| **Real-time** | **Yes** ✅ | No | Yes |
| **Free tier** | 200 leads | 1,000-2,500 leads | 11,700 leads |
| **Best for** | **Real-time apps** | Batch jobs | Direct integration |

## Monthly Cost Examples

### 1,000 leads/month
- HasData: $2.10 (or FREE with credits!)
- Apify: $2-5 (or FREE with $5 credit)
- Google Maps: $17 (or FREE with $200 credit)

### 10,000 leads/month
- HasData: $21
- Apify: $20-50
- Google Maps: $170 (or FREE with $200 credit)

### 100,000 leads/month
- HasData: $210
- Apify: $200-500
- Google Maps: $1,700

## Why HasData is Better

### vs Apify
- ✅ **15-30x faster** (2s vs 30-60s)
- ✅ **Real-time** (no polling)
- ✅ **Simpler code** (single API call)
- ✅ **Same cost**

### vs Google Maps API
- ✅ **8x cheaper** ($0.002 vs $0.017)
- ✅ **No setup hassle** (no Google Cloud)
- ✅ **No API key restrictions**
- ⚠️ Smaller free tier (200 vs 11,700 leads)

## Tips for Saving Credits

1. **Cache results**: Don't re-search the same query
2. **Limit results**: Only request what you need
3. **Monitor usage**: Check dashboard regularly
4. **Batch queries**: Process multiple searches efficiently

## Need More Credits?

- Upgrade to paid plan ($49/mo = 12,000 leads)
- Contact sales for custom pricing
- Use multiple accounts (not recommended)

## API Documentation

- HasData Docs: https://docs.hasdata.com
- Google Maps API: https://docs.hasdata.com/apis/google-maps/search
- Dashboard: https://hasdata.com/dashboard
- Support: support@hasdata.com

## Integration Support

HasData integrates with:
- ✅ Zapier
- ✅ Make (Integromat)
- ✅ n8n
- ✅ LangChain
- ✅ Custom APIs

Enjoy ultra-fast lead discovery! 🚀
