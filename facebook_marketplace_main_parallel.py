#!/usr/bin/env python3
"""
Facebook Marketplace Scraper - Parallel Execution
Scrapes listings from Facebook Marketplace using multiple parallel workers for faster execution.
"""

import os
import sys
import time
import threading
from datetime import datetime
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config_facebook_marketplace as config
from playwright.sync_api import sync_playwright
from utils.facebook_marketplace_scraper import (
    login_to_facebook,
    build_marketplace_url,
    extract_listings_from_search_page,
    close_popup_dialogs,
    scroll_page
)
from utils.facebook_marketplace_data_utils import (
    save_listings_to_csv,
    deduplicate_listings,
    print_statistics,
    export_to_json
)
from models.facebook_marketplace_listing import FacebookMarketplaceListing

# Thread-safe list to collect all listings
all_listings_lock = threading.Lock()
all_listings = []


def scrape_page_range(worker_id: int, start_page: int, end_page: int, search_params: dict) -> int:
    """
    Worker function to scrape a range of pages.

    Args:
        worker_id: Worker identifier
        start_page: Starting page number
        end_page: Ending page number
        search_params: Search parameters dict

    Returns:
        Number of listings scraped
    """
    global all_listings

    worker_listings = []

    print(f"\n[Worker {worker_id}] Starting - Pages {start_page} to {end_page}")

    # Create browser for this worker
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=config.HEADLESS)
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    page = context.new_page()

    try:
        # Login to Facebook
        login_to_facebook(page, config.FB_EMAIL, config.FB_PASSWORD)

        # Build search URL
        city = search_params.get('city', config.DEFAULT_CITY)
        category = search_params.get('category', config.DEFAULT_CATEGORY)

        marketplace_url = build_marketplace_url(
            city=city,
            category=category,
            query=search_params.get('query', ''),
            max_price=search_params.get('max_price'),
            min_price=search_params.get('min_price'),
            min_year=search_params.get('min_year'),
            max_year=search_params.get('max_year'),
            min_mileage=search_params.get('min_mileage'),
            max_mileage=search_params.get('max_mileage'),
            transmission=search_params.get('transmission', ''),
            make=search_params.get('make', ''),
            model=search_params.get('model', ''),
            radius=search_params.get('radius'),
            sort_by=search_params.get('sort_by')
        )

        # Navigate to marketplace
        page.goto(marketplace_url)
        time.sleep(3)

        # Scrape pages in assigned range
        for page_num in range(start_page, end_page + 1):
            try:
                print(f"[Worker {worker_id}] Scraping page {page_num}...")

                # Extract listings
                listings = extract_listings_from_search_page(page, scroll=True)

                print(f"[Worker {worker_id}] Page {page_num}: Found {len(listings)} listings")

                # Convert to Pydantic models
                for listing in listings:
                    try:
                        validated = FacebookMarketplaceListing(**listing)
                        worker_listings.append(validated)
                    except Exception as e:
                        print(f"[Worker {worker_id}] Validation error: {e}")

                # If fewer listings, might be at end
                if len(listings) < config.EXPECTED_LISTINGS_PER_PAGE / 2:
                    print(f"[Worker {worker_id}] Reached end of listings at page {page_num}")
                    break

                # Scroll to load next page
                if page_num < end_page:
                    scroll_page(page, num_scrolls=config.MAX_SCROLLS)
                    time.sleep(2)

            except Exception as e:
                print(f"[Worker {worker_id}] Error on page {page_num}: {e}")
                continue

    except Exception as e:
        print(f"[Worker {worker_id}] Fatal error: {e}")

    finally:
        browser.close()
        playwright.stop()

    # Add to global list (thread-safe)
    with all_listings_lock:
        all_listings.extend(worker_listings)

    print(f"[Worker {worker_id}] Completed - Scraped {len(worker_listings)} listings")

    return len(worker_listings)


def main():
    """
    Main function for parallel scraping.
    """
    global all_listings

    print("\n" + "="*80)
    print("FACEBOOK MARKETPLACE SCRAPER - PARALLEL MODE")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    # ========================================================================
    # CONFIGURATION
    # ========================================================================

    CITY = config.DEFAULT_CITY
    CATEGORY = config.DEFAULT_CATEGORY
    MAX_PAGES = config.DEFAULT_MAX_PAGES
    NUM_WORKERS = config.NUM_WORKERS

    # Search parameters
    search_params = {
        'city': CITY,
        'category': CATEGORY,
        'query': config.DEFAULT_SEARCH_QUERY,
        'max_price': config.DEFAULT_MAX_PRICE,
        'min_price': config.DEFAULT_MIN_PRICE,
        'radius': config.DEFAULT_RADIUS,
        'sort_by': config.DEFAULT_SORT_BY,
    }

    # Vehicle-specific parameters
    if CATEGORY == 'vehicles':
        search_params.update({
            'min_year': config.DEFAULT_MIN_YEAR,
            'max_year': config.DEFAULT_MAX_YEAR,
            'min_mileage': config.DEFAULT_MIN_MILEAGE,
            'max_mileage': config.DEFAULT_MAX_MILEAGE,
            'transmission': config.DEFAULT_TRANSMISSION,
            'make': config.DEFAULT_MAKE,
            'model': config.DEFAULT_MODEL,
        })

    # ========================================================================
    # DISPLAY CONFIGURATION
    # ========================================================================
    print("SEARCH CONFIGURATION:")
    print(f"  City:              {CITY}")
    print(f"  Category:          {CATEGORY}")
    print(f"  Max Pages:         {MAX_PAGES}")
    print(f"  Parallel Workers:  {NUM_WORKERS}")
    print(f"  Search Query:      {search_params.get('query', 'N/A')}")
    print(f"  Price Range:       ${search_params.get('min_price', 0):,} - ${search_params.get('max_price', 0):,}")

    if CATEGORY == 'vehicles':
        print(f"  Year Range:        {search_params.get('min_year')} - {search_params.get('max_year')}")
        print(f"  Make:              {search_params.get('make', 'Any')}")
        print(f"  Model:             {search_params.get('model', 'Any')}")

    print(f"\n  Facebook Email:    {config.FB_EMAIL if config.FB_EMAIL else 'NOT SET'}")

    if not config.FB_EMAIL or not config.FB_PASSWORD:
        print("\n" + "!"*80)
        print("WARNING: Facebook credentials not set!")
        print("Please set FB_EMAIL and FB_PASSWORD in your .env file")
        print("!"*80 + "\n")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return

    print("="*80 + "\n")

    # ========================================================================
    # DISTRIBUTE WORK AMONG WORKERS
    # ========================================================================
    pages_per_worker = MAX_PAGES // NUM_WORKERS
    remainder = MAX_PAGES % NUM_WORKERS

    work_assignments = []
    current_page = 1

    for worker_id in range(1, NUM_WORKERS + 1):
        # Distribute remainder among first workers
        pages_for_this_worker = pages_per_worker + (1 if worker_id <= remainder else 0)
        start_page = current_page
        end_page = current_page + pages_for_this_worker - 1

        work_assignments.append({
            'worker_id': worker_id,
            'start_page': start_page,
            'end_page': end_page,
            'total_pages': pages_for_this_worker
        })

        current_page = end_page + 1

    print("WORK DISTRIBUTION:")
    for assignment in work_assignments:
        print(f"  Worker {assignment['worker_id']}: "
              f"Pages {assignment['start_page']}-{assignment['end_page']} "
              f"({assignment['total_pages']} pages)")

    print("\n" + "="*80 + "\n")

    # ========================================================================
    # START PARALLEL SCRAPING
    # ========================================================================
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        # Submit all workers with staggered starts
        futures = []
        for i, assignment in enumerate(work_assignments):
            # Stagger worker starts to avoid rate limiting
            time.sleep(config.WORKER_START_DELAY * i)

            future = executor.submit(
                scrape_page_range,
                assignment['worker_id'],
                assignment['start_page'],
                assignment['end_page'],
                search_params
            )
            futures.append(future)

        # Wait for all workers to complete
        total_scraped = 0
        for future in as_completed(futures):
            try:
                count = future.result()
                total_scraped += count
            except Exception as e:
                print(f"Worker error: {e}")

    # ========================================================================
    # POST-PROCESSING
    # ========================================================================
    print("\n" + "="*80)
    print("ALL WORKERS COMPLETED - Processing results...")
    print("="*80 + "\n")

    if not all_listings:
        print("\n❌ No listings found. Please check your search parameters.")
        return

    # Deduplicate
    print(f"Total listings collected: {len(all_listings)}")
    unique_listings = deduplicate_listings(all_listings)

    # Save to CSV
    print(f"\nSaving listings to CSV...")
    csv_file = save_listings_to_csv(unique_listings, config.OUTPUT_FILE, append=False)

    # Export to JSON
    json_file = config.OUTPUT_FILE.replace('.csv', '.json')
    print(f"Exporting to JSON...")
    export_to_json(unique_listings, json_file)

    # Print statistics
    print_statistics(unique_listings)

    # ========================================================================
    # COMPLETION
    # ========================================================================
    end_time = time.time()
    duration = end_time - start_time

    print("\n" + "="*80)
    print("PARALLEL SCRAPING COMPLETED!")
    print("="*80)
    print(f"Total Time:         {duration:.2f} seconds ({duration/60:.2f} minutes)")
    print(f"Workers Used:       {NUM_WORKERS}")
    print(f"Pages Scraped:      {MAX_PAGES}")
    print(f"Listings Scraped:   {len(unique_listings)}")
    print(f"Rate:               {len(unique_listings)/duration:.2f} listings/sec")
    print(f"CSV File:           {csv_file}")
    print(f"JSON File:          {json_file}")
    print(f"End Time:           {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user (Ctrl+C)")
        print("Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
