#!/usr/bin/env python3
"""
Test script for Facebook Marketplace scraper.
Tests basic functionality with a small number of listings.
"""

import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config_facebook_marketplace as config
from utils.facebook_marketplace_scraper import scrape_facebook_marketplace
from utils.facebook_marketplace_data_utils import (
    save_listings_to_csv,
    print_statistics,
    export_to_json
)


def main():
    """
    Test the Facebook Marketplace scraper with minimal settings.
    """
    print("\n" + "="*80)
    print("FACEBOOK MARKETPLACE SCRAPER - TEST MODE")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    # ========================================================================
    # TEST CONFIGURATION - Scrape only 1 page for quick testing
    # ========================================================================

    CITY = 'Los Angeles'  # Change to your preferred city
    CATEGORY = 'vehicles'  # Test with vehicles category
    MAX_PAGES = 1  # Only scrape 1 page for testing

    # Minimal search parameters
    search_params = {
        'max_price': 20000,  # Reasonable price range for testing
        'min_price': 5000,
        'radius': 25,
    }

    # Vehicle-specific for testing
    if CATEGORY == 'vehicles':
        search_params.update({
            'min_year': 2015,
            'max_year': 2024,
        })

    print("TEST CONFIGURATION:")
    print(f"  City:         {CITY}")
    print(f"  Category:     {CATEGORY}")
    print(f"  Max Pages:    {MAX_PAGES} (test mode)")
    print(f"  Price Range:  ${search_params['min_price']:,} - ${search_params['max_price']:,}")

    if not config.FB_EMAIL or not config.FB_PASSWORD:
        print("\n" + "!"*80)
        print("WARNING: Facebook credentials not set in .env file")
        print("Add the following to your .env file:")
        print("  FB_EMAIL=your_email@example.com")
        print("  FB_PASSWORD=your_password")
        print("!"*80 + "\n")
        response = input("Continue with limited functionality? (y/n): ")
        if response.lower() != 'y':
            print("Exiting test...")
            return

    print("="*80 + "\n")
    print("Starting test scrape...\n")

    # ========================================================================
    # RUN TEST SCRAPE
    # ========================================================================

    try:
        # Scrape listings
        listings = scrape_facebook_marketplace(
            city=CITY,
            category=CATEGORY,
            max_pages=MAX_PAGES,
            **search_params
        )

        if not listings:
            print("\n❌ TEST FAILED: No listings found")
            print("Possible reasons:")
            print("  1. Facebook credentials not set or invalid")
            print("  2. No listings match the search criteria")
            print("  3. Facebook structure has changed (CSS selectors need update)")
            print("  4. Network issues or rate limiting")
            return

        print(f"\n✓ TEST PASSED: Successfully scraped {len(listings)} listings")

        # Save test results
        test_csv = 'test_facebook_marketplace_listings.csv'
        test_json = 'test_facebook_marketplace_listings.json'

        save_listings_to_csv(listings, test_csv, append=False)
        export_to_json(listings, test_json)

        # Print statistics
        print_statistics(listings)

        # Display sample listings
        print("\n" + "="*80)
        print("SAMPLE LISTINGS")
        print("="*80)
        for i, listing in enumerate(listings[:3], 1):
            print(f"\n{i}. {listing.title}")
            print(f"   Price:     {listing.price}")
            print(f"   Location:  {listing.location}")
            if listing.mileage:
                print(f"   Mileage:   {listing.mileage}")
            print(f"   URL:       {listing.listing_url}")

        print("\n" + "="*80)
        print("\n✓ TEST COMPLETED SUCCESSFULLY!")
        print(f"\nTest results saved to:")
        print(f"  - {test_csv}")
        print(f"  - {test_json}")
        print("\nYou can now run the full scraper:")
        print("  python facebook_marketplace_main.py")
        print("  python facebook_marketplace_main_parallel.py  (faster)")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        print("\nPlease check:")
        print("  1. Facebook credentials in .env file")
        print("  2. Network connection")
        print("  3. Playwright is installed: playwright install")
        return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
