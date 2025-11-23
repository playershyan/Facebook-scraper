#!/usr/bin/env python3
"""
Facebook Marketplace Scraper - Main Entry Point
Scrapes listings from Facebook Marketplace with customizable search parameters.
"""

import os
import sys
import time
from datetime import datetime
from typing import List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config_facebook_marketplace as config
from utils.facebook_marketplace_scraper import (
    scrape_facebook_marketplace,
    build_marketplace_url
)
from utils.facebook_marketplace_data_utils import (
    save_listings_to_csv,
    deduplicate_listings,
    print_statistics,
    export_to_json
)
from models.facebook_marketplace_listing import FacebookMarketplaceListing


def main():
    """
    Main function to scrape Facebook Marketplace.
    """
    print("\n" + "="*80)
    print("FACEBOOK MARKETPLACE SCRAPER")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    # ========================================================================
    # CONFIGURATION
    # ========================================================================
    # Customize these parameters for your search

    CITY = config.DEFAULT_CITY  # 'Los Angeles', 'New York', 'Chicago', etc.
    CATEGORY = config.DEFAULT_CATEGORY  # 'vehicles', 'search', 'property', etc.
    MAX_PAGES = config.DEFAULT_MAX_PAGES  # Number of pages to scrape

    # Search parameters (optional)
    search_params = {
        'query': config.DEFAULT_SEARCH_QUERY,  # Search keyword
        'max_price': config.DEFAULT_MAX_PRICE,
        'min_price': config.DEFAULT_MIN_PRICE,
        'radius': config.DEFAULT_RADIUS,  # miles
        'sort_by': config.DEFAULT_SORT_BY,
    }

    # Vehicle-specific parameters (only for category='vehicles')
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
    print(f"  Search Query:      {search_params.get('query', 'N/A')}")
    print(f"  Price Range:       ${search_params.get('min_price', 0):,} - ${search_params.get('max_price', 0):,}")
    print(f"  Radius:            {search_params.get('radius', 0)} miles")

    if CATEGORY == 'vehicles':
        print(f"  Year Range:        {search_params.get('min_year', 'N/A')} - {search_params.get('max_year', 'N/A')}")
        print(f"  Mileage Range:     {search_params.get('min_mileage', 0):,} - {search_params.get('max_mileage', 0):,} miles")
        print(f"  Transmission:      {search_params.get('transmission', 'Any')}")
        print(f"  Make:              {search_params.get('make', 'Any')}")
        print(f"  Model:             {search_params.get('model', 'Any')}")

    print(f"  Output File:       {config.OUTPUT_FILE}")
    print(f"\n  Facebook Email:    {config.FB_EMAIL if config.FB_EMAIL else 'NOT SET'}")
    print(f"  Facebook Password: {'*' * len(config.FB_PASSWORD) if config.FB_PASSWORD else 'NOT SET'}")

    # Warning if credentials not set
    if not config.FB_EMAIL or not config.FB_PASSWORD:
        print("\n" + "!"*80)
        print("WARNING: Facebook credentials not set!")
        print("Please set FB_EMAIL and FB_PASSWORD in your .env file")
        print("Some features may not work without login")
        print("!"*80 + "\n")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            return

    print("="*80 + "\n")

    # ========================================================================
    # START SCRAPING
    # ========================================================================
    start_time = time.time()

    try:
        # Scrape listings
        listings = scrape_facebook_marketplace(
            city=CITY,
            category=CATEGORY,
            max_pages=MAX_PAGES,
            **search_params
        )

        if not listings:
            print("\n❌ No listings found. Please check your search parameters.")
            return

        # Deduplicate listings
        print(f"\nRemoving duplicates...")
        unique_listings = deduplicate_listings(listings)

        # Save to CSV
        print(f"\nSaving listings to CSV...")
        csv_file = save_listings_to_csv(unique_listings, config.OUTPUT_FILE, append=False)

        # Export to JSON (optional)
        json_file = config.OUTPUT_FILE.replace('.csv', '.json')
        print(f"\nExporting to JSON...")
        export_to_json(unique_listings, json_file)

        # Print statistics
        print_statistics(unique_listings)

    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return

    # ========================================================================
    # COMPLETION
    # ========================================================================
    end_time = time.time()
    duration = end_time - start_time

    print("\n" + "="*80)
    print("SCRAPING COMPLETED SUCCESSFULLY!")
    print("="*80)
    print(f"Total Time:         {duration:.2f} seconds ({duration/60:.2f} minutes)")
    print(f"Listings Scraped:   {len(unique_listings)}")
    print(f"CSV File:           {csv_file}")
    print(f"JSON File:          {json_file}")
    print(f"End Time:           {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    # Display sample listings
    if unique_listings:
        print("\n" + "="*80)
        print("SAMPLE LISTINGS (First 5)")
        print("="*80)
        for i, listing in enumerate(unique_listings[:5], 1):
            print(f"\n{i}. {listing.title}")
            print(f"   Price:     {listing.price}")
            print(f"   Location:  {listing.location}")
            print(f"   URL:       {listing.listing_url}")
            if listing.mileage:
                print(f"   Mileage:   {listing.mileage}")
        print("\n" + "="*80 + "\n")


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
