# Setting Up Apify for Lead Discovery

The Research Agent now uses Apify's Google Maps Scraper instead of the Google Maps API directly. This can be cheaper and has a FREE tier!

## Why Apify?

### Cost Comparison

| Method | Cost per Lead | Free Tier |
|--------|---------------|-----------|
| **Apify** | **$0.002-0.005** | **$5/month FREE** |
| Google Maps API | $0.017 | $200/month |

With Apify, you can scrape ~1,000-2,500 leads for FREE each month! 🎉

### Benefits
- ✅ Much cheaper ($0.002 vs $0.017 per lead)
- ✅ FREE tier ($5 credit/month)
- ✅ No API key setup hassle
- ✅ More data fields available
- ✅ Better rate limits

## Step 1: Create Apify Account

1. Go to **Apify**: https://apify.com/sign-up

2. Sign up (free account)

3. You'll get **$5 free credit per month** automatically

## Step 2: Get Your API Token

1. Go to **Settings** → **Integrations**: https://console.apify.com/account/integrations

2. Copy your **API token** (starts with `apify_api_...`)

## Step 3: Add to .env

Add your token to the `.env` file in the project root:

```bash
APIFY_API_KEY=apify_api_...your-token-here...
```

## Step 4: Test It

```bash
cd agents/research
python example.py
```

You should see:
```
🌍 Searching for 5 leads...
   Apify run started: abc123xyz
✅ Found 5 leads
```

## Apify Pricing

### Free Tier
- **$5 credit per month** (renews monthly)
- ~1,000-2,500 leads per month FREE
- Perfect for testing and small-scale use

### Paid Plans
- **Starter**: $49/month (includes $49 credit)
- **Team**: $499/month (includes $499 credit)
- **Pay as you go**: $0.25 per compute unit

### Cost per Lead
- **Typical**: $0.002-0.005 per lead
- **10 leads**: ~$0.02-0.05
- **100 leads**: ~$0.20-0.50
- **1,000 leads**: ~$2-5

Much cheaper than Google Maps API! 💰

## What Data You Get

Apify's Google Maps Scraper provides:
- ✅ Business name
- ✅ Phone number
- ✅ Address
- ✅ Website
- ✅ Rating (1-5 stars)
- ✅ Review count
- ✅ Business hours
- ✅ Categories
- ✅ Plus/minus code
- ✅ GPS coordinates

## How It Works

1. **Start Actor Run**: Sends search query to Apify
2. **Scraping**: Apify scrapes Google Maps (takes 30-60s)
3. **Poll Status**: Agent checks if scraping is complete
4. **Get Results**: Downloads scraped data
5. **Transform**: Converts to our lead format

## Performance

- **Time**: 30-60 seconds for 10 leads (slower than API but cheaper)
- **Cost**: $0.002-0.005 per lead (8-10x cheaper!)
- **Quality**: Same data as Google Maps API

## Free Tier Limits

With $5/month free credit:
- ~1,000-2,500 leads per month
- Unlimited API calls
- No rate limits
- Renews monthly

## Troubleshooting

### "APIFY_API_KEY not set"
→ Make sure you added the key to `.env` in the project root

### "API token not valid"
→ Check that your token starts with `apify_api_`
→ Make sure you copied the entire token

### "Actor run failed"
→ Check your Apify dashboard for error details
→ You might have run out of credits

### "Run timed out"
→ Apify scraping can take 1-3 minutes for large queries
→ Try reducing `lead_count` or wait longer

### Check Your Credits
→ Go to: https://console.apify.com/billing
→ See remaining credit balance

## Comparison: Apify vs Google Maps API

| Feature | Apify | Google Maps API |
|---------|-------|-----------------|
| **Cost/lead** | $0.002-0.005 | $0.017 |
| **Free tier** | $5/month | $200/month |
| **Speed** | 30-60s | 5-10s |
| **Setup** | Easy | Moderate |
| **Data quality** | Excellent | Excellent |
| **Rate limits** | None | 50 req/sec |
| **Best for** | Cost-conscious | Speed-critical |

## Monthly Cost Examples

### 1,000 leads/month
- Apify: $2-5 (or FREE with $5 credit!)
- Google Maps: $17

### 10,000 leads/month
- Apify: $20-50
- Google Maps: $170

### 100,000 leads/month
- Apify: $200-500
- Google Maps: $1,700

## Switching Back to Google Maps API

If you need faster results, you can switch back:

1. Uncomment the old code in `search.py`
2. Set `GOOGLE_MAPS_API_KEY` in `.env`
3. Remove `APIFY_API_KEY` requirement

## Actor Details

We use: **Google Maps Scraper** by Apify
- Actor ID: `nwua9Gu5YrADL7ZDj`
- Docs: https://apify.com/nwua9Gu5YrADL7ZDj/google-maps-scraper
- Maintained by Apify (official)

## Tips for Saving Credits

1. **Cache results**: Don't re-scrape the same query
2. **Batch queries**: Process multiple searches together
3. **Limit results**: Only scrape what you need
4. **Monitor usage**: Check dashboard regularly

## Need More Credits?

- Upgrade to paid plan
- Use multiple free accounts (not recommended)
- Optimize queries to reduce scraping time

## Support

- Apify Docs: https://docs.apify.com
- Get API Token: https://console.apify.com/account/integrations
- Billing: https://console.apify.com/billing
- Support: support@apify.com

Enjoy cheaper lead discovery! 🚀
