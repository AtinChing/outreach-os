# Getting Your FREE Gemini API Key

The Research Agent now uses Google's Gemini 1.5 Flash model, which is FREE with generous quotas!

## Step 1: Get Your API Key

1. Go to **Google AI Studio**: https://aistudio.google.com/app/apikey

2. Click **"Get API key"** or **"Create API key"**

3. Select a Google Cloud project (or create a new one)

4. Copy your API key (starts with `AIza...`)

## Step 2: Add to .env

Add your key to the `.env` file in the project root:

```bash
GEMINI_API_KEY=AIzaSy...your-key-here...
```

## Step 3: Test It

```bash
cd agents/research
python example.py
```

You should see:
```
🧠 Enriching leads with Gemini...
  [1/5] Enriching Coffee Shop Name...
  ✅ Enriched 5 leads
```

## Gemini 1.5 Flash Features

- **Model**: `gemini-1.5-flash`
- **Cost**: FREE (up to 15 requests per minute, 1,500 per day)
- **Speed**: ~2-3 seconds per lead
- **Quality**: Excellent for business analysis

## Free Tier Limits

- **Rate limit**: 15 requests per minute
- **Daily limit**: 1,500 requests per day
- **Monthly limit**: 1 million tokens per month

This means you can process:
- **15 leads per minute** (900/hour)
- **1,500 leads per day**
- **~45,000 leads per month**

All completely FREE! 🎉

## Quota Exceeded?

If you hit rate limits, the agent will automatically retry with backoff. For higher volumes, you can:

1. **Upgrade to paid tier** (still very cheap)
2. **Use multiple API keys** (rotate between them)
3. **Add delays** between requests

## Comparison: Gemini vs Claude

| Feature | Gemini 1.5 Flash | Claude 3.5 Sonnet |
|---------|------------------|-------------------|
| Cost | FREE | $0.001/lead |
| Speed | ~2-3s | ~2-3s |
| Quality | Excellent | Excellent |
| Rate Limit | 15/min | 50/min |
| Daily Limit | 1,500 | Unlimited |

For most use cases, Gemini Flash is perfect and FREE!

## Troubleshooting

### "GEMINI_API_KEY not set"
→ Make sure you added the key to `.env` in the project root

### "API key not valid"
→ Check that your key starts with `AIza`
→ Make sure you copied the entire key

### "Resource exhausted"
→ You've hit the rate limit (15/min)
→ The agent will automatically retry
→ Or wait a minute and try again

### "Permission denied"
→ Enable the Generative Language API in Google Cloud Console
→ Go to: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com

## Need Help?

- Gemini API Docs: https://ai.google.dev/gemini-api/docs
- Get API Key: https://aistudio.google.com/app/apikey
- Pricing: https://ai.google.dev/pricing

Enjoy your FREE AI-powered lead enrichment! 🚀
