import asyncio
import os
from datetime import datetime
from typing import List, Set

from crawl4ai import AsyncWebCrawler
from dotenv import load_dotenv

from config_riyasewana import (
    BASE_URL,
    TOTAL_PAGES,
    LISTINGS_PER_PAGE,
    REQUIRED_KEYS,
)
from utils.riyasewana_data_utils import (
    is_complete_listing,
    is_duplicate_listing,
    load_existing_urls,
    save_listings_to_csv,
)
from utils.riyasewana_scraper import (
    extract_listing_details,
    fetch_listing_urls_from_page,
    get_browser_config,
    get_llm_strategy,
)

load_dotenv()

# Configuration
OUTPUT_CSV = "riyasewana_listings.csv"
BATCH_SAVE_INTERVAL = 10  # Save to CSV every N listings
PAGE_DELAY = 2  # Seconds to wait between pages
LISTING_DELAY = 1  # Seconds to wait between listing detail requests
MAX_RETRIES = 3  # Maximum retries for failed requests


async def scrape_listings():
    """
    Main function to scrape all car listings from riyasewana.com.
    """
    print("=" * 60)
    print("Riyasewana Car Listings Scraper")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print(f"Total pages to scrape: {TOTAL_PAGES}")
    print(f"Expected listings per page: {LISTINGS_PER_PAGE}")
    print(f"Output file: {OUTPUT_CSV}")
    print("=" * 60)
    print()
    
    # Check for GROQ API key
    if not os.getenv("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY not found in environment variables!")
        print("Please create a .env file with your GROQ_API_KEY.")
        return
    
    # Initialize configurations
    browser_config = get_browser_config(headless=True)
    llm_strategy = get_llm_strategy()
    session_id = f"riyasewana_crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Load existing URLs to avoid duplicates (for resuming interrupted scrapes)
    seen_urls = load_existing_urls(OUTPUT_CSV)
    print(f"Loaded {len(seen_urls)} existing URLs (resuming from previous scrape)")
    print()
    
    # Statistics
    stats = {
        'pages_processed': 0,
        'total_urls_found': 0,
        'listings_extracted': 0,
        'listings_saved': 0,
        'errors': 0,
        'duplicates_skipped': 0,
    }
    
    all_listings = []
    failed_urls = []
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        print("Starting crawl...")
        print()
        
        # Loop through all pages
        for page_num in range(1, TOTAL_PAGES + 1):
            try:
                print(f"\n[{page_num}/{TOTAL_PAGES}] Processing page {page_num}...")
                
                # Extract listing URLs from search page
                listing_urls = await fetch_listing_urls_from_page(
                    crawler,
                    page_num,
                    BASE_URL,
                    session_id,
                )
                
                if not listing_urls:
                    print(f"  ⚠ No listing URLs found on page {page_num}")
                    stats['errors'] += 1
                    await asyncio.sleep(PAGE_DELAY)
                    continue
                
                stats['total_urls_found'] += len(listing_urls)
                print(f"  ✓ Found {len(listing_urls)} listing URLs")
                
                # Process each listing URL
                for idx, listing_url in enumerate(listing_urls, 1):
                    # Skip if already processed
                    if is_duplicate_listing(listing_url, seen_urls):
                        print(f"    [{idx}/{len(listing_urls)}] ⏭ Skipping duplicate: {listing_url}")
                        stats['duplicates_skipped'] += 1
                        continue
                    
                    # Retry logic for failed extractions
                    listing_data = None
                    for attempt in range(MAX_RETRIES):
                        try:
                            listing_data = await extract_listing_details(
                                crawler,
                                listing_url,
                                llm_strategy,
                                session_id,
                            )
                            
                            if listing_data:
                                break  # Success, exit retry loop
                                
                        except Exception as e:
                            if attempt < MAX_RETRIES - 1:
                                print(f"    [{idx}/{len(listing_urls)}] ⚠ Error on attempt {attempt + 1}, retrying...")
                                await asyncio.sleep(LISTING_DELAY * (attempt + 1))
                            else:
                                print(f"    [{idx}/{len(listing_urls)}] ✗ Failed after {MAX_RETRIES} attempts: {listing_url}")
                                failed_urls.append(listing_url)
                                stats['errors'] += 1
                    
                    # Process extracted listing
                    if listing_data:
                        # Validate completeness
                        if is_complete_listing(listing_data, REQUIRED_KEYS):
                            seen_urls.add(listing_url)
                            all_listings.append(listing_data)
                            stats['listings_extracted'] += 1
                            print(f"    [{idx}/{len(listing_urls)}] ✓ Extracted: {listing_data.get('title', 'N/A')[:50]}...")
                        else:
                            missing_keys = [key for key in REQUIRED_KEYS if key not in listing_data or not listing_data[key]]
                            print(f"    [{idx}/{len(listing_urls)}] ⚠ Incomplete listing (missing: {', '.join(missing_keys)})")
                            # Still save URL to avoid re-scraping
                            seen_urls.add(listing_url)
                    else:
                        print(f"    [{idx}/{len(listing_urls)}] ✗ Failed to extract data")
                    
                    # Batch save to CSV periodically
                    if len(all_listings) >= BATCH_SAVE_INTERVAL:
                        save_listings_to_csv(all_listings, OUTPUT_CSV)
                        stats['listings_saved'] += len(all_listings)
                        all_listings = []  # Clear batch
                        print(f"  💾 Saved batch to {OUTPUT_CSV}")
                    
                    # Rate limiting between listing requests
                    await asyncio.sleep(LISTING_DELAY)
                
                stats['pages_processed'] += 1
                
                # Progress summary
                if page_num % 10 == 0:
                    print(f"\n📊 Progress Summary:")
                    print(f"   Pages processed: {stats['pages_processed']}/{TOTAL_PAGES}")
                    print(f"   Total URLs found: {stats['total_urls_found']}")
                    print(f"   Listings extracted: {stats['listings_extracted']}")
                    print(f"   Duplicates skipped: {stats['duplicates_skipped']}")
                    print(f"   Errors: {stats['errors']}")
                    print()
                
                # Rate limiting between pages
                await asyncio.sleep(PAGE_DELAY)
                
            except Exception as e:
                print(f"  ✗ Error processing page {page_num}: {e}")
                stats['errors'] += 1
                await asyncio.sleep(PAGE_DELAY)
                continue
        
        # Save any remaining listings
        if all_listings:
            save_listings_to_csv(all_listings, OUTPUT_CSV)
            stats['listings_saved'] += len(all_listings)
        
        # Final statistics
        print("\n" + "=" * 60)
        print("Crawl Complete!")
        print("=" * 60)
        print(f"Pages processed: {stats['pages_processed']}/{TOTAL_PAGES}")
        print(f"Total URLs found: {stats['total_urls_found']}")
        print(f"Listings extracted: {stats['listings_extracted']}")
        print(f"Listings saved: {stats['listings_saved']}")
        print(f"Duplicates skipped: {stats['duplicates_skipped']}")
        print(f"Errors: {stats['errors']}")
        print(f"Output file: {OUTPUT_CSV}")
        
        if failed_urls:
            print(f"\n⚠ {len(failed_urls)} URLs failed to extract. Saving to failed_urls.txt...")
            with open("failed_urls.txt", "w", encoding="utf-8") as f:
                for url in failed_urls:
                    f.write(url + "\n")
            print("Failed URLs saved to failed_urls.txt")
        
        # Display LLM usage statistics
        print("\nLLM Usage Statistics:")
        llm_strategy.show_usage()
        print()


async def main():
    """Entry point of the script."""
    try:
        await scrape_listings()
    except KeyboardInterrupt:
        print("\n\n⚠ Scraping interrupted by user. Progress saved to CSV.")
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

