# config_riyasewana.py

BASE_URL = "https://riyasewana.com/search/cars"
LISTING_BASE_URL = "https://riyasewana.com"  # Base URL for listing pages
TOTAL_PAGES = 635
LISTINGS_PER_PAGE = 44

# Output configuration
OUTPUT_DIR = "output"  # Folder for CSV files
OUTPUT_CSV = "riyasewana_listings.csv"  # Default output filename (will be saved in OUTPUT_DIR)

# CSS selectors for extracting listing URLs from search pages
# These will need to be adjusted based on actual page structure
LISTING_LINK_SELECTOR = "a[href*='/buy/']"  # Adjust based on actual HTML structure

# CSS selector for listing details page
LISTING_DETAILS_SELECTOR = "body"  # We'll extract all content and use LLM to parse

# Required keys for a complete listing
REQUIRED_KEYS = [
    "title",
    "posted_date",
    "posted_by",
    "contact_info",
    "listing_url",
]

