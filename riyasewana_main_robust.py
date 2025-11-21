"""
Robust parallel scraper with comprehensive error handling and recovery.
Handles network errors, API errors, crashes, and can resume from checkpoints.
"""
import asyncio
import os
import sys
import signal
from datetime import datetime
from pathlib import Path
from typing import List, Set, Tuple, Optional, Dict

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
from utils.session_manager import get_session_manager, reset_session_manager
from utils.error_handler import ScraperErrorHandler, ErrorType, handle_crash_recovery, safe_operation

load_dotenv()

# Configuration
OUTPUT_DIR = "output"  # Folder for CSV files
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "riyasewana_listings.csv")  # Save to output folder
BATCH_SAVE_INTERVAL = 5  # Save to CSV every N listings (more frequent)
CHECKPOINT_INTERVAL = 10  # Save checkpoint every N pages

# Create output directory if it doesn't exist
Path(OUTPUT_DIR).mkdir(exist_ok=True)
PAGE_DELAY = 5
LISTING_DELAY = 3
MAX_RETRIES = 3
NUM_WORKERS = 10
WORKER_STAGGER_DELAY = 3

# Checkpoint and recovery
SESSIONS_DIR = "sessions"
PROGRESS_FILE = "scraper_progress.json"


# Global variables for cleanup on crash
session_manager = None
progress_tracker = None
current_checkpoint_data = {}


def signal_handler(signum, frame):
    """Handle system signals (Ctrl+C, termination, etc.)."""
    print("\n\n[INTERRUPT] Signal received. Saving checkpoint and cleaning up...")
    
    if session_manager and current_checkpoint_data:
        try:
            handle_crash_recovery(session_manager, current_checkpoint_data)
            if session_manager.current_session:
                session_manager.end_session(status="interrupted")
        except Exception as e:
            print(f"[INTERRUPT] Error during cleanup: {e}")
    
    sys.exit(0)


# Register signal handlers for graceful shutdown
try:
    if sys.platform == 'win32':
        # Windows signal handling
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    else:
        # Unix/Linux signal handling
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGHUP, signal_handler)
except Exception as e:
    print(f"Warning: Could not register signal handlers: {e}")


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
    session_manager=None,
    error_handler=None,
    resume_data: Optional[Dict] = None,
) -> dict:
    """
    Worker function that scrapes a range of pages with error handling.
    
    Args:
        worker_id: Unique ID for this worker
        start_page: First page to scrape (inclusive)
        end_page: Last page to scrape (inclusive)
        output_csv: Output CSV filename
        progress_tracker: Progress tracker instance
        session_manager: Session manager instance
        error_handler: Error handler instance
        resume_data: Optional resume data to continue from checkpoint
    
    Returns:
        Dictionary with statistics for this worker
    """
    print(f"\n{'='*60}")
    print(f"Worker {worker_id} starting: Pages {start_page} to {end_page}")
    print(f"{'='*60}")
    
    # Initialize configurations
    browser_config = get_browser_config(headless=True)
    llm_strategy = get_llm_strategy() if os.getenv("GROQ_API_KEY") else None
    session_id = f"riyasewana_worker_{worker_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Load existing URLs to avoid duplicates
    seen_urls = load_existing_urls(output_csv)
    
    # If resuming, use resume data
    if resume_data:
        seen_urls.update(resume_data.get("seen_urls", set()))
        print(f"  [Worker {worker_id}] Resuming from checkpoint")
        print(f"  [Worker {worker_id}] Already processed {len(seen_urls)} URLs")
    
    # Statistics
    stats = {
        'worker_id': worker_id,
        'pages_processed': resume_data.get("stats", {}).get("pages_processed", 0) if resume_data else 0,
        'total_urls_found': resume_data.get("stats", {}).get("total_urls_found", 0) if resume_data else 0,
        'listings_extracted': resume_data.get("stats", {}).get("listings_extracted", 0) if resume_data else 0,
        'listings_saved': resume_data.get("stats", {}).get("listings_saved", 0) if resume_data else 0,
        'errors': resume_data.get("stats", {}).get("errors", 0) if resume_data else 0,
        'duplicates_skipped': resume_data.get("stats", {}).get("duplicates_skipped", 0) if resume_data else 0,
    }
    
    all_listings = []
    failed_urls = []
    total_pages_for_worker = end_page - start_page + 1
    last_checkpoint_page = resume_data.get("last_page", start_page - 1) if resume_data else start_page - 1
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Loop through assigned pages
        for page_num in range(last_checkpoint_page + 1, end_page + 1):
            try:
                print(f"\n[Worker {worker_id}] [{page_num - start_page + 1}/{total_pages_for_worker}] "
                      f"Processing page {page_num}/{TOTAL_PAGES}...")
                
                # Extract listing URLs from search page with error handling
                listing_urls = await safe_operation(
                    fetch_listing_urls_from_page,
                    error_handler,
                    checkpoint_data={
                        "last_page": page_num - 1,
                        "seen_urls": list(seen_urls),
                        "stats": stats,
                        "worker_id": worker_id,
                    },
                    crawler=crawler,
                    page_number=page_num,
                    base_url=BASE_URL,
                    session_id=session_id,
                )
                
                if not listing_urls:
                    print(f"  [Worker {worker_id}] WARNING: No listing URLs found on page {page_num}")
                    stats['errors'] += 1
                    if session_manager:
                        session_manager.update_session(
                            stats={"errors": 1},
                            error={"type": "no_urls", "message": f"No URLs found on page {page_num}"}
                        )
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

                # Process each listing URL with error handling
                for idx, listing_url in enumerate(listing_urls, 1):
                    # Skip if already processed
                    if is_duplicate_listing(listing_url, seen_urls):
                        stats['duplicates_skipped'] += 1
                        continue
                    
                    # Extract listing details with error handling
                    listing_data = await safe_operation(
                        extract_listing_details,
                        error_handler,
                        checkpoint_data={
                            "last_page": page_num - 1,
                            "last_url": listing_url,
                            "seen_urls": list(seen_urls),
                            "stats": stats,
                            "worker_id": worker_id,
                        },
                        crawler=crawler,
                        listing_url=listing_url,
                        llm_strategy=llm_strategy,
                        session_id=session_id,
                        use_llm_fallback=llm_strategy is not None,
                    )
                    
                    # Process extracted listing
                    if listing_data:
                        if is_complete_listing(listing_data, REQUIRED_KEYS):
                            seen_urls.add(listing_url)
                            all_listings.append(listing_data)
                            stats['listings_extracted'] += 1

                            # ✅ REAL-TIME UPDATE: Update progress after EACH listing
                            if progress_tracker:
                                progress_tracker.update_listings(
                                    found=stats['total_urls_found'],
                                    extracted=stats['listings_extracted'],
                                    saved=stats['listings_saved'],
                                    duplicates_skipped=stats['duplicates_skipped'],
                                )
                        else:
                            seen_urls.add(listing_url)  # Mark as processed even if incomplete
                    else:
                        failed_urls.append(listing_url)

                    # Save to CSV frequently to prevent data loss
                    if len(all_listings) >= BATCH_SAVE_INTERVAL:
                        try:
                            save_listings_to_csv(all_listings, output_csv)
                            stats['listings_saved'] += len(all_listings)

                            # Update session stats
                            if session_manager:
                                session_manager.update_session(
                                    stats={"listings_saved": len(all_listings)}
                                )

                            # ✅ REAL-TIME UPDATE: Update progress after batch save
                            if progress_tracker:
                                progress_tracker.update_listings(
                                    found=stats['total_urls_found'],
                                    extracted=stats['listings_extracted'],
                                    saved=stats['listings_saved'],
                                    duplicates_skipped=stats['duplicates_skipped'],
                                )

                            all_listings = []
                            print(f"  [Worker {worker_id}] Saved batch to {output_csv}")
                        except Exception as e:
                            error_handler.log_error(
                                ErrorType.FILE_ERROR,
                                e,
                                {"operation": "save_listings", "worker_id": worker_id}
                            )
                    
                    await asyncio.sleep(LISTING_DELAY)
                
                stats['pages_processed'] += 1
                
                # Update progress tracker
                if progress_tracker:
                    progress_tracker.update_worker(
                        worker_id,
                        pages_processed=1,
                        urls_found=len(listing_urls),
                        listings_extracted=stats['listings_extracted'],
                        errors=stats['errors'],
                        status="running",
                    )
                    progress_tracker.update_listings(
                        found=stats['total_urls_found'],
                        extracted=stats['listings_extracted'],
                        saved=stats['listings_saved'],
                        duplicates_skipped=stats['duplicates_skipped'],
                    )
                    # Calculate total completed pages across all workers
                    total_completed = sum(
                        progress_tracker.progress["workers"].get(str(w), {}).get("pages_processed", 0)
                        for w in range(1, NUM_WORKERS + 1)
                    )
                    progress_tracker.update_work_completed(total_completed)
                
                # Save checkpoint periodically
                if (page_num - last_checkpoint_page) % CHECKPOINT_INTERVAL == 0:
                    if session_manager:
                        checkpoint_data = {
                            "last_page": page_num,
                            "seen_urls": list(seen_urls),
                            "stats": stats.copy(),
                            "worker_id": worker_id,
                            "failed_urls": failed_urls,
                        }
                        session_manager.mark_resume_point(page_num, seen_urls, stats)
                        print(f"  [Worker {worker_id}] Checkpoint saved at page {page_num}")
                
                # Update global checkpoint data
                global current_checkpoint_data
                current_checkpoint_data = {
                    "last_page": page_num,
                    "seen_urls": list(seen_urls),
                    "stats": stats.copy(),
                    "worker_id": worker_id,
                }
                
                await asyncio.sleep(PAGE_DELAY)
                
            except KeyboardInterrupt:
                print(f"\n[Worker {worker_id}] Interrupted by user")
                raise
            except Exception as e:
                error_type = error_handler.classify_error(e) if error_handler else ErrorType.UNKNOWN_ERROR
                if error_handler:
                    error_handler.log_error(
                        error_type,
                        e,
                        {"worker_id": worker_id, "page_num": page_num}
                    )
                
                stats['errors'] += 1
                
                # Save checkpoint on error
                if session_manager:
                    session_manager.mark_resume_point(page_num - 1, seen_urls, stats)
                
                await asyncio.sleep(PAGE_DELAY)
                continue
        
        # Save any remaining listings
        if all_listings:
            try:
                save_listings_to_csv(all_listings, output_csv)
                stats['listings_saved'] += len(all_listings)
            except Exception as e:
                if error_handler:
                    error_handler.log_error(ErrorType.FILE_ERROR, e, {"operation": "final_save"})
        
        # Update session - mark worker as completed
        if session_manager:
            session_manager.update_session(
                stats={
                    "pages_processed": stats['pages_processed'],
                    "total_urls_found": stats['total_urls_found'],
                    "listings_extracted": stats['listings_extracted'],
                    "listings_saved": stats['listings_saved'],
                    "errors": stats['errors'],
                }
            )
        
        print(f"\n[Worker {worker_id}] Completed: Pages {start_page} to {end_page}")
        
        return stats


async def scrape_listings_parallel(resume_session_id: Optional[str] = None):
    """
    Main function to coordinate parallel scraping with error handling and recovery.
    
    Args:
        resume_session_id: Optional session ID to resume from
    """
    global session_manager, progress_tracker, current_checkpoint_data
    
    print("=" * 60)
    print("Riyasewana Car Listings Scraper - ROBUST PARALLEL MODE")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print(f"Total pages to scrape: {TOTAL_PAGES}")
    print(f"Number of parallel workers: {NUM_WORKERS}")
    print(f"Output file: {OUTPUT_CSV}")
    print(f"Sessions directory: {SESSIONS_DIR}")
    print("=" * 60)
    print()
    
    # Initialize session manager
    session_manager = reset_session_manager(SESSIONS_DIR)
    
    # Initialize error handler
    error_handler = ScraperErrorHandler(session_manager=session_manager, max_retries=MAX_RETRIES)
    
    # Initialize progress tracker
    progress_tracker = reset_progress_tracker(PROGRESS_FILE)
    progress_tracker.set_total_work(TOTAL_PAGES, "pages")
    progress_tracker.set_status("running")
    
    # Create or resume session
    if resume_session_id:
        print(f"Resuming session: {resume_session_id}")
        session = session_manager.get_session(resume_session_id)
        if not session:
            print(f"ERROR: Session {resume_session_id} not found!")
            return
        
        session_manager.current_session = session
        resume_data = session_manager.get_resume_data(resume_session_id)
        print(f"Resume data: {resume_data}")
    else:
        # Create new session
        session_id = session_manager.create_session(
            metadata={
                "total_pages": TOTAL_PAGES,
                "num_workers": NUM_WORKERS,
                "base_url": BASE_URL,
                "output_csv": OUTPUT_CSV,
            }
        )
        resume_data = None
    
    # Distribute pages among workers
    page_ranges = distribute_pages(TOTAL_PAGES, NUM_WORKERS)
    
    print("Page Distribution:")
    for i, (start, end) in enumerate(page_ranges, 1):
        print(f"  Worker {i}: Pages {start} to {end} ({end - start + 1} pages)")
    print()
    
    # Create delayed worker wrapper
    async def delayed_worker(worker_id, start_page, end_page, delay, worker_resume_data=None):
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
            session_manager=session_manager,
            error_handler=error_handler,
            resume_data=worker_resume_data,
        )
    
    # Create tasks for all workers
    print(f"Starting {NUM_WORKERS} workers with staggered delays...")
    print(f"Each worker will start {WORKER_STAGGER_DELAY} seconds after the previous one\n")
    
    tasks = []
    for worker_id, (start_page, end_page) in enumerate(page_ranges, 1):
        delay = (worker_id - 1) * WORKER_STAGGER_DELAY
        task = delayed_worker(worker_id, start_page, end_page, delay)
        tasks.append(task)
    
    # Run all workers in parallel
    print("Launching all workers...\n")
    
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
    except KeyboardInterrupt:
        print("\n\n[INTERRUPT] Scraping interrupted by user")
        if session_manager:
            session_manager.end_session(status="interrupted")
            session_manager.mark_resume_point(
                current_checkpoint_data.get("last_page", 0),
                set(current_checkpoint_data.get("seen_urls", [])),
                current_checkpoint_data.get("stats", {})
            )
        raise
    
    # Aggregate results
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
            if error_handler:
                error_handler.log_error(ErrorType.UNKNOWN_ERROR, result, {"worker_id": i})
            continue
        
        if isinstance(result, dict):
            total_stats['pages_processed'] += result['pages_processed']
            total_stats['total_urls_found'] += result['total_urls_found']
            total_stats['listings_extracted'] += result['listings_extracted']
            total_stats['listings_saved'] += result['listings_saved']
            total_stats['errors'] += result['errors']
            total_stats['duplicates_skipped'] += result['duplicates_skipped']
    
    # Update progress tracker
    if progress_tracker:
        progress_tracker.update_work_completed(total_stats['pages_processed'])
        progress_tracker.set_status("completed")
    
    # End session
    if session_manager:
        session_manager.update_session(stats=total_stats)
        session_manager.end_session(status="completed")
    
    # Final summary
    print("\n" + "=" * 60)
    print("TOTAL SUMMARY")
    print("=" * 60)
    print(f"Total pages processed: {total_stats['pages_processed']}/{TOTAL_PAGES}")
    print(f"Total URLs found: {total_stats['total_urls_found']}")
    print(f"Total listings extracted: {total_stats['listings_extracted']}")
    print(f"Total listings saved: {total_stats['listings_saved']}")
    print(f"Total duplicates skipped: {total_stats['duplicates_skipped']}")
    print(f"Total errors: {total_stats['errors']}")
    
    # Error summary
    if error_handler:
        error_summary = error_handler.get_error_summary()
        print(f"\nError Summary:")
        print(f"  Total errors: {error_summary['total_errors']}")
        for error_type, count in error_summary['by_type'].items():
            print(f"  {error_type}: {count}")
    
    print(f"\nOutput file: {OUTPUT_CSV}")
    print(f"Session data: {SESSIONS_DIR}/")
    print("=" * 60)
    print()


async def main():
    """Entry point of the script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Riyasewana Parallel Scraper with Recovery')
    parser.add_argument('--resume', type=str, help='Resume from session ID')
    args = parser.parse_args()
    
    try:
        await scrape_listings_parallel(resume_session_id=args.resume)
    except KeyboardInterrupt:
        print("\n\n[WARNING] Scraping interrupted. Progress saved to checkpoint.")
        if session_manager:
            session_manager.end_session(status="interrupted")
    except Exception as e:
        print(f"\n\n[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        
        if session_manager:
            session_manager.end_session(status="error", error={
                "type": "fatal_error",
                "message": str(e),
                "traceback": traceback.format_exc(),
            })
        raise


if __name__ == "__main__":
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
    
    asyncio.run(main())

