"""
Quick test script - scrapes only 1 page for testing.
Saves CSV files to 'output' folder.
"""
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

from crawl4ai import AsyncWebCrawler
from dotenv import load_dotenv

from config_riyasewana import BASE_URL, REQUIRED_KEYS
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
from utils.progress_tracker import reset_progress_tracker
from utils.session_manager import reset_session_manager
from utils.error_handler import ScraperErrorHandler, ErrorType, safe_operation

load_dotenv()

# Test configuration - only 1 page
TEST_PAGES = 1
OUTPUT_DIR = "output"  # Folder for CSV files
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "test_output_1_page.csv")
PROGRESS_FILE = "scraper_progress.json"
SESSIONS_DIR = "sessions"
PAGE_DELAY = 3
LISTING_DELAY = 2

# Create output directory if it doesn't exist
Path(OUTPUT_DIR).mkdir(exist_ok=True)


async def test_scrape_1_page():
    """Test scraping 1 page."""
    print("=" * 60)
    print("TEST: Scraping 1 Page")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print(f"Pages to scrape: {TEST_PAGES}")
    print(f"Output folder: {OUTPUT_DIR}/")
    print(f"Output file: {OUTPUT_CSV}")
    print("=" * 60)
    print()
    
    # Initialize session manager and progress tracker
    session_manager = reset_session_manager(SESSIONS_DIR)
    progress_tracker = reset_progress_tracker(PROGRESS_FILE)
    progress_tracker.set_total_work(TEST_PAGES, "pages")
    progress_tracker.set_status("running")
    
    # Create session
    session_id = session_manager.create_session(
        metadata={
            "total_pages": TEST_PAGES,
            "test_run": True,
        }
    )
    
    # Initialize error handler
    error_handler = ScraperErrorHandler(session_manager=session_manager)
    
    # Initialize browser
    browser_config = get_browser_config(headless=True)
    llm_strategy = get_llm_strategy() if os.getenv("GROQ_API_KEY") else None
    session_crawl_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Load existing URLs
    seen_urls = load_existing_urls(OUTPUT_CSV)
    
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
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        for page_num in range(1, TEST_PAGES + 1):
            try:
                print(f"\n[Page {page_num}/{TEST_PAGES}] Processing...")
                
                # Extract listing URLs from search page
                listing_urls = await safe_operation(
                    fetch_listing_urls_from_page,
                    error_handler,
                    crawler=crawler,
                    page_number=page_num,
                    base_url=BASE_URL,
                    session_id=session_crawl_id,
                )

                if not listing_urls:
                    print(f"  No URLs found on page {page_num}")
                    stats['errors'] += 1
                    continue

                stats['total_urls_found'] += len(listing_urls)
                print(f"  Found {len(listing_urls)} listing URLs")
                
                # Update progress immediately after finding URLs
                progress_tracker.update_listings(
                    found=stats['total_urls_found'],
                    extracted=stats['listings_extracted'],
                    saved=len(all_listings),
                )
                
                # Process all listings (removed [:3] limit for full extraction)
                for idx, listing_url in enumerate(listing_urls, 1):
                    if is_duplicate_listing(listing_url, seen_urls):
                        stats['duplicates_skipped'] += 1
                        continue

                    print(f"    [{idx}/{len(listing_urls)}] Extracting: {listing_url[:60]}...")

                    listing_data = await safe_operation(
                        extract_listing_details,
                        error_handler,
                        crawler=crawler,
                        listing_url=listing_url,
                        llm_strategy=llm_strategy,
                        session_id=session_crawl_id,
                        use_llm_fallback=llm_strategy is not None,
                    )

                    if listing_data and is_complete_listing(listing_data, REQUIRED_KEYS):
                        seen_urls.add(listing_url)
                        all_listings.append(listing_data)
                        stats['listings_extracted'] += 1
                        print(f"      ✓ Extracted: {listing_data.get('title', 'N/A')[:50]}...")

                        # ✅ REAL-TIME UPDATE: Update progress after EACH listing
                        progress_tracker.update_listings(
                            found=stats['total_urls_found'],
                            extracted=stats['listings_extracted'],
                            saved=len(all_listings),
                        )
                    else:
                        print(f"      ✗ Failed to extract complete data")

                    await asyncio.sleep(LISTING_DELAY)
                
                stats['pages_processed'] += 1
                
                # Update progress tracker
                progress_tracker.update_work_completed(page_num)
                progress_tracker.update_listings(
                    found=stats['total_urls_found'],
                    extracted=stats['listings_extracted'],
                    saved=len(all_listings),
                )
                
                # Save checkpoint
                if session_manager:
                    session_manager.mark_resume_point(page_num, seen_urls, stats)
                
                await asyncio.sleep(PAGE_DELAY)
                
            except Exception as e:
                print(f"  Error on page {page_num}: {e}")
                stats['errors'] += 1
                continue
        
        # Save all listings
        if all_listings:
            save_listings_to_csv(all_listings, OUTPUT_CSV)
            stats['listings_saved'] = len(all_listings)
            print(f"\n✓ Saved {len(all_listings)} listings to {OUTPUT_CSV}")
        
        # Update final stats
        progress_tracker.set_status("completed")
        if session_manager:
            session_manager.update_session(stats=stats)
            session_manager.end_session(status="completed")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)
        print(f"Pages processed: {stats['pages_processed']}/{TEST_PAGES}")
        print(f"URLs found: {stats['total_urls_found']}")
        print(f"Listings extracted: {stats['listings_extracted']}")
        print(f"Listings saved: {stats['listings_saved']}")
        print(f"Output folder: {OUTPUT_DIR}/")
        print(f"Output file: {OUTPUT_CSV}")
        print("=" * 60)


async def main():
    """Entry point."""
    try:
        await test_scrape_1_page()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPT] Test interrupted")
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if sys.platform == 'win32':
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
    
    asyncio.run(main())

