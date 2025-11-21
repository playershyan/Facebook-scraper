# Quick Start Guide - Riyasewana Scraper

## Prerequisites
1. ✅ Python environment is set up (already done)
2. ✅ Dependencies are installed (already done)
3. ⚠️ Need `.env` file with `GROQ_API_KEY`

## Step 1: Create .env File

If you haven't already, create a `.env` file in the project root:

```bash
copy ENV_TEMPLATE.txt .env
```

Then edit `.env` and add your GROQ API key:
```
GROQ_API_KEY=your_actual_api_key_here
```

Get your API key from: https://console.groq.com/

## Step 2: Install Playwright Browsers

```powershell
cd deepseek-ai-web-crawler-main
venv\Scripts\activate
playwright install
```

## Step 3: Test First (Recommended)

Before running the full scrape, test with a single page:

```powershell
python test_riyasewana.py
```

This will:
- Test if it can find listing URLs on page 1
- Test if it can extract details from one listing
- Help you verify the selectors are correct

## Step 4: Run the Scraper

Once testing is successful, run the full scraper:

```powershell
python riyasewana_main.py
```

## Expected Output

- **CSV File**: `riyasewana_listings.csv` - All extracted listings
- **Failed URLs**: `failed_urls.txt` - URLs that failed (if any)

## Important Notes

⚠️ **Time**: The full scrape will take approximately 12-24 hours for 635 pages × 44 listings

⚠️ **Rate Limiting**: The scraper includes delays between requests to be respectful. Don't reduce delays too much or you may get blocked.

⚠️ **Resume Capability**: If the scraper is interrupted, it will resume from where it left off (skips already-processed URLs)

⚠️ **API Costs**: Each listing uses the LLM API. For ~27,940 listings, monitor your API usage.

## Adjusting Configuration

If selectors don't work, you may need to adjust them. See `RIYASEWANA_README.md` for details.

## Troubleshooting

1. **No listing URLs found**: Check CSS selectors in `utils/riyasewana_scraper.py`
2. **LLM extraction fails**: Verify your GROQ_API_KEY is correct
3. **Website blocks you**: Increase delays in `riyasewana_main.py`

