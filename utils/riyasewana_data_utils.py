import csv
import os
from typing import List, Set

try:
    import fcntl  # Unix/Linux only
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False  # Windows

from models.listing import Listing


def is_duplicate_listing(listing_url: str, seen_urls: Set[str]) -> bool:
    """Check if a listing URL has already been processed."""
    return listing_url in seen_urls


def is_complete_listing(listing: dict, required_keys: List[str]) -> bool:
    """Check if a listing has all required fields."""
    return all(key in listing and listing[key] for key in required_keys)


def save_listings_to_csv(listings: List[dict], filename: str):
    """
    Save listings to a CSV file with file locking for thread-safe writes.
    Automatically creates output directory if it doesn't exist.
    
    Args:
        listings: List of listing dictionaries
        filename: Output CSV filename (can include folder path)
    """
    if not listings:
        return
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Use field names from the Listing model
    fieldnames = Listing.model_fields.keys()
    
    # Check if file exists
    file_exists = os.path.exists(filename)
    
    # Open file with locking for thread-safe writing
    # Note: On Windows, we rely on OS-level file locking and append mode
    # which should prevent most race conditions
    mode = "a" if file_exists else "w"
    
    try:
        with open(filename, mode=mode, newline="", encoding="utf-8") as file:
            # On Unix/Linux, acquire exclusive lock
            if HAS_FCNTL and os.name != 'nt':
                fcntl.flock(file.fileno(), fcntl.LOCK_EX)
            
            try:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                # Write header only if file is new
                if not file_exists:
                    writer.writeheader()
                
                # Filter listings to only include fields in the model
                filtered_listings = []
                for listing in listings:
                    filtered_listing = {key: listing.get(key, '') for key in fieldnames}
                    filtered_listings.append(filtered_listing)
                
                writer.writerows(filtered_listings)
            finally:
                # Release lock on Unix/Linux
                if HAS_FCNTL and os.name != 'nt':
                    fcntl.flock(file.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        print(f"Error saving listings to CSV: {e}")
        raise


def load_existing_urls(filename: str) -> Set[str]:
    """
    Load existing listing URLs from CSV to avoid duplicates.
    
    Args:
        filename: CSV filename to read from
    
    Returns:
        Set of existing listing URLs
    """
    seen_urls = set()
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if 'listing_url' in row:
                    seen_urls.add(row['listing_url'])
    except FileNotFoundError:
        pass  # File doesn't exist yet, that's fine
    
    return seen_urls

