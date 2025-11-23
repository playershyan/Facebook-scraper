import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Set, Tuple

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
from utils.progress_tracker import get_progress_tracker, reset_progress_tracker

load_dotenv()

# Configuration
OUTPUT_DIR = "output"  # Folder for CSV files
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "riyasewana_listings.csv")  # Save to output folder
BATCH_SAVE_INTERVAL = 10  # Save to CSV every N listings

# Create output directory if it doesn't exist
from pathlib import Path
Path(OUTPUT_DIR).mkdir(exist_ok=True)

# Rate limiting delays - increased for parallel workers to be respectful
# These delays help avoid getting rate-limited by the website
PAGE_DELAY = 5  # Seconds to wait between pages (increased from 2 for parallel workers)
LISTING_DELAY = 3  # Seconds to wait between listing detail requests (increased for safety)
MAX_RETRIES = 3  # Maximum retries for failed requests
NUM_WORKERS = 10  # Number of parallel scrapers

# Additional safety: staggered worker start times to avoid all workers hitting at once
WORKER_STAGGER_DELAY = 3  # Seconds to stagger each worker's start time


def distribute_pages(total_pages: int, num_workers: int, custom_distribution: bool = True) -> List[Tuple[int, int]]:
    """
    Distributes pages among workers.
    
    Args:
        total_pages: Total number of pages to scrape
        num_workers: Number of parallel workers
        custom_distribution: If True, uses custom distribution (9 workers × 67, 1 worker × remainder)
                            If False, distributes evenly
    
    Returns:
        List of (start_page, end_page) tuples for each worker
    """
    if custom_distribution and total_pages == 635 and num_workers == 10:
        # Custom distribution: 9 workers × 67 pages, 1 worker × remainder
        pages_per_worker = 67
        remainder = total_pages - (pages_per_worker * (num_workers - 1))
        
        ranges = []
        start_page = 1
        
        # First 9 workers get 67 pages each
        for i in range(num_workers - 1):
            end_page = start_page + pages_per_worker - 1
            ranges.append((start_page, end_page))
            start_page = end_page + 1
        
        # Last worker gets remainder (32 pages)
        end_page = start_page + remainder - 1
        ranges.append((start_page, end_page))
        
        return ranges
    else:
        # Even distribution
        pages_per_worker = total_pages // num_workers
        remainder = total_pages % num_workers
        
        ranges = []
        start_page = 1
        
        for i in range(num_workers):
            # Distribute remainder pages among first workers
            pages_for_this_worker = pages_per_worker + (1 if i < remainder else 0)
            end_page = start_page + pages_for_this_worker - 1
            
            ranges.append((start_page, end_page))
            start_page = end_page + 1
        
        return ranges


async def scrape_listings_worker(
    worker_id: int,
    start_page: int,
    end_page: int,
    output_csv: str,
    progress_tracker=None,
) -> dict:
    """
    Worker function that scrapes a range of pages.
    
    Args:
        worker_id: Unique ID for this worker
        start_page: First page to scrape (inclusive)
        end_page: Last page to scrape (inclusive)
        output_csv: Output CSV filename
    
    Returns:
        Dictionary with statistics for this worker
    """
    print(f"\n{'='*60}")
    print(f"Worker {worker_id} starting: Pages {start_page} to {end_page}")
    print(f"{'='*60}")
    
    # Check for GROQ API key (needed for fallback)
    if not os.getenv("GROQ_API_KEY"):
        print(f"Worker {worker_id}: WARNING - GROQ_API_KEY not found. LLM fallback disabled.")
    
    # Initialize configurations
    browser_config = get_browser_config(headless=True)
    llm_strategy = get_llm_strategy() if os.getenv("GROQ_API_KEY") else None
    session_id = f"riyasewana_worker_{worker_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Load existing URLs to avoid duplicates
    seen_urls = load_existing_urls(output_csv)
    
    # Statistics
    stats = {
        'worker_id': worker_id,
        'pages_processed': 0,
        'total_urls_found': 0,
        'listings_extracted': 0,
        'listings_saved': 0,
        'errors': 0,
        'duplicates_skipped': 0,
    }
    
    all_listings = []
    failed_urls = []
    total_pages_for_worker = end_page - start_page + 1
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Loop through assigned pages
        for page_num in range(start_page, end_page + 1):
            try:
                print(f"\n[Worker {worker_id}] [{page_num - start_page + 1}/{total_pages_for_worker}] "
                      f"Processing page {page_num}/{TOTAL_PAGES}...")
                
                # Extract listing URLs from search page
                listing_urls = await fetch_listing_urls_from_page(
                    crawler,
                    page_num,
                    BASE_URL,
                    session_id,
                )
                
                if not listing_urls:
                    print(f"  [Worker {worker_id}] WARNING: No listing URLs found on page {page_num}")
                    stats['errors'] += 1
                    await asyncio.sleep(PAGE_DELAY)
                    continue
                
                stats['total_urls_found'] += len(listing_urls)
                print(f"  [Worker {worker_id}] Found {len(listing_urls)} listing URLs")

                # ✅ REAL-TIME UPDATE: Update progress immediately after finding URLs
                if progress_tracker:
                    progress_tracker.update_listings(
                        found=stats['total_urls_found'],
                        extracted=stats['listings_extracted'],
                        saved=stats['listings_saved'],
                        duplicates_skipped=stats['duplicates_skipped'],
                    )

                # Process each listing URL
                for idx, listing_url in enumerate(listing_urls, 1):
                    # Skip if already processed (check both local and global seen_urls)
                    if is_duplicate_listing(listing_url, seen_urls):
                        print(f"    [Worker {worker_id}] [{idx}/{len(listing_urls)}] "
                              f"Skipping duplicate: {listing_url[:60]}...")
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
                                use_llm_fallback=llm_strategy is not None,
                            )
                            
                            if listing_data:
                                break  # Success, exit retry loop
                                
                        except Exception as e:
                            if attempt < MAX_RETRIES - 1:
                                print(f"    [Worker {worker_id}] [{idx}/{len(listing_urls)}] "
                                      f"Error on attempt {attempt + 1}, retrying...")
                                await asyncio.sleep(LISTING_DELAY * (attempt + 1))
                            else:
                                print(f"    [Worker {worker_id}] [{idx}/{len(listing_urls)}] "
                                      f"Failed after {MAX_RETRIES} attempts")
                                failed_urls.append(listing_url)
                                stats['errors'] += 1
                    
                    # Process extracted listing
                    if listing_data:
                        # Validate completeness
                        if is_complete_listing(listing_data, REQUIRED_KEYS):
                            seen_urls.add(listing_url)
                            all_listings.append(listing_data)
                            stats['listings_extracted'] += 1
                            title_preview = listing_data.get('title', 'N/A')[:50]
                            print(f"    [Worker {worker_id}] [{idx}/{len(listing_urls)}] "
                                  f"Extracted: {title_preview}...")

                            # ✅ REAL-TIME UPDATE: Update progress after EACH listing
                            if progress_tracker:
                                progress_tracker.update_listings(
                                    found=stats['total_urls_found'],
                                    extracted=stats['listings_extracted'],
                                    saved=stats['listings_saved'],
                                    duplicates_skipped=stats['duplicates_skipped'],
                                )
                        else:
                            missing_keys = [key for key in REQUIRED_KEYS
                                          if key not in listing_data or not listing_data[key]]
                            print(f"    [Worker {worker_id}] [{idx}/{len(listing_urls)}] "
                                  f"Incomplete (missing: {', '.join(missing_keys)})")
                            seen_urls.add(listing_url)  # Still mark as processed
                    else:
                        print(f"    [Worker {worker_id}] [{idx}/{len(listing_urls)}] "
                              f"Failed to extract data")

                    # Batch save to CSV periodically
                    if len(all_listings) >= BATCH_SAVE_INTERVAL:
                        # Use file locking to prevent race conditions
                        save_listings_to_csv(all_listings, output_csv)
                        stats['listings_saved'] += len(all_listings)

                        # ✅ REAL-TIME UPDATE: Update progress after batch save
                        if progress_tracker:
                            progress_tracker.update_listings(
                                found=stats['total_urls_found'],
                                extracted=stats['listings_extracted'],
                                saved=stats['listings_saved'],
                                duplicates_skipped=stats['duplicates_skipped'],
                            )

                        all_listings = []  # Clear batch
                        print(f"  [Worker {worker_id}] Saved batch to {output_csv}")
                    
                    # Rate limiting between listing requests
                    await asyncio.sleep(LISTING_DELAY)
                
                stats['pages_processed'] += 1
                
                # Update progress tracker after each page
                if progress_tracker:
                    # Update worker stats
                    progress_tracker.update_worker(
                        worker_id,
                        pages_processed=1,
                        urls_found=len(listing_urls),
                        listings_extracted=stats['listings_extracted'],
                        errors=stats['errors'],
                        status="running",
                    )
                    # Update overall listings stats
                    progress_tracker.update_listings(
                        found=stats['total_urls_found'],
                        extracted=stats['listings_extracted'],
                        saved=stats['listings_saved'],
                        duplicates_skipped=stats['duplicates_skipped'],
                    )
                    # Calculate total completed pages from all workers
                    total_completed = sum(
                        progress_tracker.progress["workers"].get(str(w), {}).get("pages_processed", 0)
                        for w in range(1, NUM_WORKERS + 1)
                    )
                    progress_tracker.update_work_completed(total_completed)
                
                # Progress summary every 10 pages
                if (page_num - start_page + 1) % 10 == 0:
                    print(f"\n[Worker {worker_id}] Progress Summary:")
                    print(f"   Pages processed: {stats['pages_processed']}/{total_pages_for_worker}")
                    print(f"   Total URLs found: {stats['total_urls_found']}")
                    print(f"   Listings extracted: {stats['listings_extracted']}")
                    print(f"   Duplicates skipped: {stats['duplicates_skipped']}")
                    print(f"   Errors: {stats['errors']}")
                
                # Rate limiting between pages
                await asyncio.sleep(PAGE_DELAY)
                
            except Exception as e:
                print(f"  [Worker {worker_id}] Error processing page {page_num}: {e}")
                stats['errors'] += 1
                await asyncio.sleep(PAGE_DELAY)
                continue
        
        # Save any remaining listings
        if all_listings:
            save_listings_to_csv(all_listings, output_csv)
            stats['listings_saved'] += len(all_listings)
        
        print(f"\n[Worker {worker_id}] Completed: Pages {start_page} to {end_page}")
        print(f"  Pages processed: {stats['pages_processed']}/{total_pages_for_worker}")
        print(f"  Listings extracted: {stats['listings_extracted']}")
        
        # Update progress tracker - mark worker as completed
        if progress_tracker:
            progress_tracker.update_worker(
                worker_id,
                status="completed",
            )
        
        # Save failed URLs to worker-specific file
        if failed_urls:
            failed_file = f"failed_urls_worker_{worker_id}.txt"
            with open(failed_file, "w", encoding="utf-8") as f:
                for url in failed_urls:
                    f.write(url + "\n")
            print(f"  Failed URLs saved to {failed_file}")
    
    return stats


async def scrape_listings_parallel():
    """
    Main function to coordinate parallel scraping of all car listings.
    """
    print("=" * 60)
    print("Riyasewana Car Listings Scraper - PARALLEL MODE")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print(f"Total pages to scrape: {TOTAL_PAGES}")
    print(f"Expected listings per page: {LISTINGS_PER_PAGE}")
    print(f"Number of parallel workers: {NUM_WORKERS}")
    print(f"Output file: {OUTPUT_CSV}")
    print("=" * 60)
    print()
    
    # Initialize progress tracker
    progress_tracker = reset_progress_tracker("scraper_progress.json")
    progress_tracker.set_total_work(TOTAL_PAGES, "pages")
    progress_tracker.set_status("running")
    
    # Distribute pages among workers
    page_ranges = distribute_pages(TOTAL_PAGES, NUM_WORKERS)
    
    print("Page Distribution:")
    for i, (start, end) in enumerate(page_ranges, 1):
        print(f"  Worker {i}: Pages {start} to {end} ({end - start + 1} pages)")
    print()
    
    # Create a wrapper function that adds staggered delay before starting
    async def delayed_worker(worker_id, start_page, end_page, delay, progress_tracker):
        """Wrapper to add staggered delay before worker starts."""
        if delay > 0:
            print(f"  Worker {worker_id} will start in {delay} seconds...")
            await asyncio.sleep(delay)
        return await scrape_listings_worker(
            worker_id=worker_id,
            start_page=start_page,
            end_page=end_page,
            output_csv=OUTPUT_CSV,
            progress_tracker=progress_tracker,
        )
    
    # Create tasks for all workers with staggered start times
    # This prevents all workers from hitting the site simultaneously
    print(f"Starting {NUM_WORKERS} workers with staggered delays...")
    print(f"Each worker will start {WORKER_STAGGER_DELAY} seconds after the previous one\n")
    
    tasks = []
    for worker_id, (start_page, end_page) in enumerate(page_ranges, 1):
        delay = (worker_id - 1) * WORKER_STAGGER_DELAY  # Stagger each worker
        task = delayed_worker(
            worker_id=worker_id,
            start_page=start_page,
            end_page=end_page,
            delay=delay,
            progress_tracker=progress_tracker,
        )
        tasks.append(task)
    
    # Run all workers in parallel (they'll start with staggered delays)
    print("Launching all workers...\n")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Aggregate statistics
    print("\n" + "=" * 60)
    print("ALL WORKERS COMPLETE!")
    print("=" * 60)
    
    total_stats = {
        'pages_processed': 0,
        'total_urls_found': 0,
        'listings_extracted': 0,
        'listings_saved': 0,
        'errors': 0,
        'duplicates_skipped': 0,
    }
    
    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print(f"\nWorker {i} encountered an error: {result}")
            continue
        
        if isinstance(result, dict):
            print(f"\nWorker {result['worker_id']} Final Stats:")
            print(f"  Pages processed: {result['pages_processed']}")
            print(f"  Total URLs found: {result['total_urls_found']}")
            print(f"  Listings extracted: {result['listings_extracted']}")
            print(f"  Listings saved: {result['listings_saved']}")
            print(f"  Duplicates skipped: {result['duplicates_skipped']}")
            print(f"  Errors: {result['errors']}")
            
            total_stats['pages_processed'] += result['pages_processed']
            total_stats['total_urls_found'] += result['total_urls_found']
            total_stats['listings_extracted'] += result['listings_extracted']
            total_stats['listings_saved'] += result['listings_saved']
            total_stats['errors'] += result['errors']
            total_stats['duplicates_skipped'] += result['duplicates_skipped']
    
    # Update progress tracker with final stats
    if progress_tracker:
        progress_tracker.update_work_completed(total_stats['pages_processed'])
        progress_tracker.update_listings(
            found=total_stats['total_urls_found'],
            extracted=total_stats['listings_extracted'],
            saved=total_stats['listings_saved'],
            duplicates_skipped=total_stats['duplicates_skipped'],
            failed=len([f for f in os.listdir('.') if f.startswith('failed_urls_worker_')]),
        )
        progress_tracker.update_errors(total_stats['errors'])
        progress_tracker.set_status("completed")
    
    print("\n" + "=" * 60)
    print("TOTAL SUMMARY")
    print("=" * 60)
    print(f"Total pages processed: {total_stats['pages_processed']}/{TOTAL_PAGES}")
    print(f"Total URLs found: {total_stats['total_urls_found']}")
    print(f"Total listings extracted: {total_stats['listings_extracted']}")
    print(f"Total listings saved: {total_stats['listings_saved']}")
    print(f"Total duplicates skipped: {total_stats['duplicates_skipped']}")
    print(f"Total errors: {total_stats['errors']}")
    print(f"Output file: {OUTPUT_CSV}")
    print("=" * 60)
    
    # Update progress tracker - mark as completed
    if progress_tracker:
        progress_tracker.set_status("completed")
        progress_tracker.update_work_completed(TOTAL_PAGES)
    
    # Combine failed URLs from all workers
    all_failed_urls = []
    for worker_id in range(1, NUM_WORKERS + 1):
        failed_file = f"failed_urls_worker_{worker_id}.txt"
        try:
            with open(failed_file, "r", encoding="utf-8") as f:
                all_failed_urls.extend([line.strip() for line in f if line.strip()])
        except FileNotFoundError:
            pass
    
    if all_failed_urls:
        print(f"\nTotal failed URLs: {len(all_failed_urls)}")
        with open("failed_urls.txt", "w", encoding="utf-8") as f:
            for url in all_failed_urls:
                f.write(url + "\n")
        print("All failed URLs saved to failed_urls.txt")
    
    print()


async def main():
    """Entry point of the script."""
    try:
        await scrape_listings_parallel()
    except KeyboardInterrupt:
        print("\n\n[WARNING] Scraping interrupted by user. Progress saved to CSV.")
    except Exception as e:
        print(f"\n\n[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
    
    asyncio.run(main())

