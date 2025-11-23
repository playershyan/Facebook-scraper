"""
Data utilities for Facebook Marketplace scraper.
Handles CSV export, data validation, and data processing.
"""

import csv
import os
import fcntl
from typing import List, Dict
from models.facebook_marketplace_listing import FacebookMarketplaceListing
import config_facebook_marketplace as config


def save_listings_to_csv(
    listings: List[FacebookMarketplaceListing],
    filename: str = None,
    append: bool = False
) -> str:
    """
    Save Facebook Marketplace listings to CSV file.

    Args:
        listings: List of FacebookMarketplaceListing objects
        filename: Output CSV filename (defaults to config.OUTPUT_FILE)
        append: Whether to append to existing file or overwrite

    Returns:
        Path to the saved CSV file
    """
    filename = filename or config.OUTPUT_FILE

    if not listings:
        print("No listings to save.")
        return filename

    # Convert Pydantic models to dictionaries
    data = [listing.model_dump() for listing in listings]

    # Determine write mode
    mode = 'a' if append else 'w'
    file_exists = os.path.exists(filename) and append

    try:
        with open(filename, mode, newline='', encoding='utf-8') as csvfile:
            # Lock file for thread-safe writing
            try:
                fcntl.flock(csvfile.fileno(), fcntl.LOCK_EX)
            except:
                pass  # Windows doesn't support fcntl

            # Get all possible field names from the first listing
            fieldnames = list(data[0].keys())

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header only if file is new or we're overwriting
            if not file_exists:
                writer.writeheader()

            # Write data
            for row in data:
                writer.writerow(row)

            # Unlock file
            try:
                fcntl.flock(csvfile.fileno(), fcntl.LOCK_UN)
            except:
                pass

        print(f"\n✓ Successfully saved {len(listings)} listings to {filename}")

    except Exception as e:
        print(f"\n✗ Error saving to CSV: {e}")
        raise

    return filename


def load_listings_from_csv(filename: str = None) -> List[Dict]:
    """
    Load listings from CSV file.

    Args:
        filename: CSV filename to load (defaults to config.OUTPUT_FILE)

    Returns:
        List of dictionaries containing listing data
    """
    filename = filename or config.OUTPUT_FILE

    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return []

    listings = []

    try:
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            listings = list(reader)

        print(f"Loaded {len(listings)} listings from {filename}")

    except Exception as e:
        print(f"Error loading from CSV: {e}")

    return listings


def deduplicate_listings(
    listings: List[FacebookMarketplaceListing],
    key: str = 'listing_url'
) -> List[FacebookMarketplaceListing]:
    """
    Remove duplicate listings based on a key field.

    Args:
        listings: List of FacebookMarketplaceListing objects
        key: Field to use for deduplication (default: 'listing_url')

    Returns:
        List of unique listings
    """
    seen = set()
    unique_listings = []

    for listing in listings:
        listing_dict = listing.model_dump()
        value = listing_dict.get(key)

        if value and value not in seen:
            seen.add(value)
            unique_listings.append(listing)

    duplicates_removed = len(listings) - len(unique_listings)
    if duplicates_removed > 0:
        print(f"Removed {duplicates_removed} duplicate listings")

    return unique_listings


def filter_listings(
    listings: List[FacebookMarketplaceListing],
    min_price: float = None,
    max_price: float = None,
    location_contains: str = None,
    title_contains: str = None
) -> List[FacebookMarketplaceListing]:
    """
    Filter listings based on criteria.

    Args:
        listings: List of FacebookMarketplaceListing objects
        min_price: Minimum price filter
        max_price: Maximum price filter
        location_contains: Filter by location substring
        title_contains: Filter by title substring

    Returns:
        Filtered list of listings
    """
    filtered = listings

    if min_price is not None or max_price is not None:
        def extract_price(price_str: str) -> float:
            """Extract numeric price from string like '$5,000' or 'Free'."""
            if not price_str or price_str.lower() == 'free':
                return 0.0
            import re
            numbers = re.findall(r'\d+', price_str.replace(',', ''))
            return float(''.join(numbers)) if numbers else 0.0

        if min_price is not None:
            filtered = [l for l in filtered if extract_price(l.price) >= min_price]

        if max_price is not None:
            filtered = [l for l in filtered if extract_price(l.price) <= max_price]

    if location_contains:
        filtered = [
            l for l in filtered
            if location_contains.lower() in l.location.lower()
        ]

    if title_contains:
        filtered = [
            l for l in filtered
            if title_contains.lower() in l.title.lower()
        ]

    print(f"Filtered {len(listings)} listings down to {len(filtered)}")

    return filtered


def get_statistics(listings: List[FacebookMarketplaceListing]) -> Dict:
    """
    Generate statistics about the scraped listings.

    Args:
        listings: List of FacebookMarketplaceListing objects

    Returns:
        Dictionary containing statistics
    """
    if not listings:
        return {
            'total_listings': 0,
            'avg_price': 0,
            'min_price': 0,
            'max_price': 0,
            'locations': [],
            'categories': []
        }

    def extract_price(price_str: str) -> float:
        """Extract numeric price from string."""
        if not price_str or price_str.lower() == 'free':
            return 0.0
        import re
        numbers = re.findall(r'\d+', price_str.replace(',', ''))
        return float(''.join(numbers)) if numbers else 0.0

    prices = [extract_price(l.price) for l in listings if l.price]
    prices = [p for p in prices if p > 0]  # Exclude free items

    locations = list(set(l.location for l in listings if l.location))
    categories = list(set(l.category for l in listings if l.category))

    stats = {
        'total_listings': len(listings),
        'listings_with_price': len(prices),
        'avg_price': sum(prices) / len(prices) if prices else 0,
        'min_price': min(prices) if prices else 0,
        'max_price': max(prices) if prices else 0,
        'unique_locations': len(locations),
        'locations': locations[:10],  # Top 10 locations
        'unique_categories': len(categories),
        'categories': categories
    }

    return stats


def print_statistics(listings: List[FacebookMarketplaceListing]) -> None:
    """
    Print statistics about the scraped listings.

    Args:
        listings: List of FacebookMarketplaceListing objects
    """
    stats = get_statistics(listings)

    print(f"\n{'='*80}")
    print(f"SCRAPING STATISTICS")
    print(f"{'='*80}")
    print(f"Total Listings:        {stats['total_listings']}")
    print(f"Listings with Price:   {stats['listings_with_price']}")
    print(f"Average Price:         ${stats['avg_price']:,.2f}")
    print(f"Min Price:             ${stats['min_price']:,.2f}")
    print(f"Max Price:             ${stats['max_price']:,.2f}")
    print(f"Unique Locations:      {stats['unique_locations']}")
    print(f"Unique Categories:     {stats['unique_categories']}")

    if stats['locations']:
        print(f"\nTop Locations:")
        for loc in stats['locations']:
            print(f"  - {loc}")

    if stats['categories']:
        print(f"\nCategories:")
        for cat in stats['categories']:
            print(f"  - {cat}")

    print(f"{'='*80}\n")


def validate_listings(listings: List[Dict]) -> tuple[List[FacebookMarketplaceListing], List[Dict]]:
    """
    Validate listings against the Pydantic model.

    Args:
        listings: List of dictionaries containing listing data

    Returns:
        Tuple of (valid_listings, invalid_listings)
    """
    valid = []
    invalid = []

    for listing in listings:
        try:
            validated = FacebookMarketplaceListing(**listing)
            valid.append(validated)
        except Exception as e:
            invalid.append({
                'data': listing,
                'error': str(e)
            })

    if invalid:
        print(f"\nWarning: {len(invalid)} listings failed validation")

    return valid, invalid


def merge_csv_files(input_files: List[str], output_file: str = None) -> str:
    """
    Merge multiple CSV files into one, removing duplicates.

    Args:
        input_files: List of CSV filenames to merge
        output_file: Output filename (defaults to config.OUTPUT_FILE)

    Returns:
        Path to the merged CSV file
    """
    output_file = output_file or config.OUTPUT_FILE

    all_listings = []

    # Load all CSV files
    for filename in input_files:
        if os.path.exists(filename):
            listings = load_listings_from_csv(filename)
            all_listings.extend(listings)
            print(f"Loaded {len(listings)} listings from {filename}")

    # Validate and deduplicate
    valid_listings, invalid = validate_listings(all_listings)
    unique_listings = deduplicate_listings(valid_listings)

    # Save merged file
    save_listings_to_csv(unique_listings, output_file, append=False)

    print(f"\nMerged {len(input_files)} files into {output_file}")
    print(f"Total unique listings: {len(unique_listings)}")

    return output_file


def export_to_json(listings: List[FacebookMarketplaceListing], filename: str) -> str:
    """
    Export listings to JSON file.

    Args:
        listings: List of FacebookMarketplaceListing objects
        filename: Output JSON filename

    Returns:
        Path to the saved JSON file
    """
    import json

    data = [listing.model_dump() for listing in listings]

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✓ Exported {len(listings)} listings to {filename}")

    except Exception as e:
        print(f"✗ Error exporting to JSON: {e}")
        raise

    return filename
