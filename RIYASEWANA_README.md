# Riyasewana Car Listings Scraper

This scraper extracts car listing information from riyasewana.com, including:
- Title
- Posted date
- Posted by information
- Contact information
- Listing URL

## Features

- **Scalable**: Handles 635 pages × 44 listings = ~27,940 listings
- **Resumable**: Saves progress incrementally, can resume interrupted scrapes
- **Robust**: Error handling and retry logic for failed requests
- **LLM-Powered**: Uses Groq API with DeepSeek for intelligent data extraction
- **Rate-Limited**: Respectful delays between requests

## Setup

1. **Activate the virtual environment**:
   ```powershell
   cd deepseek-ai-web-crawler-main
   venv\Scripts\activate
   ```

2. **Ensure you have `.env` file with GROQ_API_KEY**:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

3. **Install Playwright browsers** (if not already done):
   ```powershell
   playwright install
   ```

## Usage

Run the scraper:
```powershell
python riyasewana_main.py
```

## Configuration

Edit `config_riyasewana.py` to adjust:
- `TOTAL_PAGES`: Total number of pages to scrape (default: 635)
- `BASE_URL`: Base URL for search pages
- `LISTING_LINK_SELECTOR`: CSS selector for listing links on search pages
- `PAGE_DELAY`: Delay between pages (seconds)
- `LISTING_DELAY`: Delay between listing detail requests (seconds)

## Output

- **CSV File**: `riyasewana_listings.csv` - Contains all extracted listings
- **Failed URLs**: `failed_urls.txt` - URLs that failed to extract (if any)

## How It Works

1. **Page Scraping**: Iterates through search pages (1-635)
   - Extracts listing URLs from each page
   - Uses CSS selectors or regex to find `/buy/` links

2. **Detail Extraction**: Visits each listing URL
   - Uses LLM to extract structured data
   - Validates completeness of extracted data

3. **Data Saving**: Saves to CSV incrementally
   - Batch saves every N listings
   - Avoids data loss on interruption

4. **Resume Capability**: 
   - Loads existing URLs from CSV
   - Skips already-processed listings

## Adjusting Selectors

If the scraper doesn't find listing URLs correctly, you may need to adjust the selectors in `utils/riyasewana_scraper.py`.

To test selectors:
1. Open the search page in a browser
2. Inspect the HTML structure
3. Find the correct selector for listing links
4. Update `extract_listing_urls_from_page()` function

Common patterns to check:
- `a[href*='/buy/']`
- `.listing-link` or `.ad-link`
- Specific class names in the HTML

## Troubleshooting

### No listing URLs found
- Check the CSS selectors in `extract_listing_urls_from_page()`
- Inspect the actual HTML structure of the search pages
- The website structure may have changed

### LLM extraction failing
- Verify your GROQ_API_KEY is correct
- Check API rate limits
- Review the extraction instruction in `get_llm_strategy()`

### Rate limiting
- Increase `PAGE_DELAY` and `LISTING_DELAY` in `riyasewana_main.py`
- Reduce concurrent requests if the website blocks you

## Performance

Expected time:
- ~27,940 listings × 1-2 seconds per listing = 7-15 hours
- With rate limiting and delays, expect 12-24 hours for complete scrape

## Notes

- The scraper saves progress incrementally, so you can stop and resume
- Failed URLs are saved to `failed_urls.txt` for manual review
- Consider running during off-peak hours to be more respectful

