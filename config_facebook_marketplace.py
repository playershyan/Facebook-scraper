"""
Configuration file for Facebook Marketplace scraper.
Contains settings for scraping Facebook Marketplace listings.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# FACEBOOK AUTHENTICATION
# ============================================================================
# IMPORTANT: Add your Facebook credentials to .env file
# FB_EMAIL=your_email@example.com
# FB_PASSWORD=your_password
FB_EMAIL = os.getenv('FB_EMAIL', '')
FB_PASSWORD = os.getenv('FB_PASSWORD', '')

# ============================================================================
# FACEBOOK MARKETPLACE URLS
# ============================================================================
FB_LOGIN_URL = "https://www.facebook.com/login/device-based/regular/login/"
FB_MARKETPLACE_BASE = "https://www.facebook.com/marketplace"

# ============================================================================
# CITY MAPPINGS
# ============================================================================
# Dictionary of supported cities and their Facebook Marketplace identifiers
# From: https://m.facebook.com/marketplace/directory/US/
CITIES = {
    'New York': 'nyc',
    'Los Angeles': 'la',
    'Las Vegas': 'vegas',
    'Chicago': 'chicago',
    'Houston': 'houston',
    'San Antonio': 'sanantonio',
    'Miami': 'miami',
    'Orlando': 'orlando',
    'San Diego': 'sandiego',
    'Arlington': 'arlington',
    'Baltimore': 'baltimore',
    'Cincinnati': 'cincinnati',
    'Denver': 'denver',
    'Fort Worth': 'fortworth',
    'Jacksonville': 'jacksonville',
    'Memphis': 'memphis',
    'Nashville': 'nashville',
    'Philadelphia': 'philly',
    'Portland': 'portland',
    'San Jose': 'sanjose',
    'Tucson': 'tucson',
    'Atlanta': 'atlanta',
    'Boston': 'boston',
    'Columbus': 'columbus',
    'Detroit': 'detroit',
    'Honolulu': 'honolulu',
    'Kansas City': 'kansascity',
    'New Orleans': 'neworleans',
    'Phoenix': 'phoenix',
    'Seattle': 'seattle',
    'Washington DC': 'dc',
    'Milwaukee': 'milwaukee',
    'Sacramento': 'sac',
    'Austin': 'austin',
    'Charlotte': 'charlotte',
    'Dallas': 'dallas',
    'El Paso': 'elpaso',
    'Indianapolis': 'indianapolis',
    'Louisville': 'louisville',
    'Minneapolis': 'minneapolis',
    'Oklahoma City': 'oklahoma',
    'Pittsburgh': 'pittsburgh',
    'San Francisco': 'sanfrancisco',
    'Tampa': 'tampa',
    'Brisbane': 'brisbane',  # Australia
}

# ============================================================================
# SEARCH PARAMETERS
# ============================================================================
DEFAULT_CITY = 'Los Angeles'
DEFAULT_CATEGORY = 'vehicles'  # 'vehicles', 'property', 'electronics', 'search' (general)
DEFAULT_SEARCH_QUERY = ''
DEFAULT_MAX_PRICE = 50000
DEFAULT_MIN_PRICE = 0
DEFAULT_RADIUS = 50  # miles

# Vehicle-specific parameters
DEFAULT_MIN_YEAR = 2010
DEFAULT_MAX_YEAR = 2024
DEFAULT_MIN_MILEAGE = 0
DEFAULT_MAX_MILEAGE = 150000
DEFAULT_TRANSMISSION = 'automatic'  # 'automatic', 'manual', or empty for all
DEFAULT_MAKE = ''  # e.g., 'honda', 'toyota', or empty for all
DEFAULT_MODEL = ''  # e.g., 'civic', 'camry', or empty for all
DEFAULT_SORT_BY = 'creation_time_descend'  # 'creation_time_descend', 'price_ascend', 'price_descend'

# ============================================================================
# SCRAPING PARAMETERS
# ============================================================================
# Number of pages to scrape
DEFAULT_MAX_PAGES = 10

# Number of listings to scrape per page (Facebook typically shows ~20-40)
EXPECTED_LISTINGS_PER_PAGE = 30

# Scroll settings for infinite scroll pages (DEPRECATED - now using random delays)
SCROLL_PAUSE_TIME = 2  # seconds (not used - kept for backward compatibility)
MAX_SCROLLS = 5  # Maximum number of scrolls per page

# ============================================================================
# ANTI-DETECTION & RATE LIMITING SETTINGS
# ============================================================================
# Random delay ranges (in seconds) to mimic human behavior
# These are used throughout the scraper to avoid bot detection

# Delays after page loads
PAGE_LOAD_DELAY_MIN = 3.0
PAGE_LOAD_DELAY_MAX = 6.0

# Delays between scrolls
SCROLL_DELAY_MIN = 1.5
SCROLL_DELAY_MAX = 4.0

# Delays between pages
PAGE_TRANSITION_DELAY_MIN = 3.0
PAGE_TRANSITION_DELAY_MAX = 8.0

# Delays for parallel workers (more conservative)
PARALLEL_PAGE_DELAY_MIN = 4.0
PARALLEL_PAGE_DELAY_MAX = 10.0

# Delay after login attempt
LOGIN_DELAY_MIN = 4.0
LOGIN_DELAY_MAX = 7.0

# Delay after interactions (clicks, form fills)
INTERACTION_DELAY_MIN = 0.5
INTERACTION_DELAY_MAX = 2.0

# ============================================================================
# PARALLEL EXECUTION
# ============================================================================
# Number of parallel workers (reduced from 5 to 3 for better stealth)
NUM_WORKERS = 3

# Delay between worker starts (seconds) to avoid rate limiting
# Increased to be more conservative
WORKER_START_DELAY = 5

# ============================================================================
# CSS SELECTORS (Facebook Marketplace structure)
# ============================================================================
# Note: These selectors may change as Facebook updates their UI
# Last verified: January 2025

# Listing container on search results page
LISTING_CONTAINER_CLASS = 'x9f619 x78zum5 x1r8uery xdt5ytf x1iyjqo2 xs83m0k x1e558r4 x150jy0e x1iorvi4 xjkvuk6 xnpuxes x291uyu x1uepa24'

# Individual listing elements
IMAGE_CLASS = 'xt7dq6l xl1xv1r x6ikm8r x10wlt62 xh8yej3'
TITLE_CLASS = 'x1lliihq x6ikm8r x10wlt62 x1n2onr6'
PRICE_CLASS = 'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x676frb x1lkfr7t x1lbecb7 x1s688f xzsf02u'
LINK_CLASS = 'x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1lku1pv'
LOCATION_MILEAGE_CLASS = 'x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft'

# Detailed listing page selectors
DESCRIPTION_CLASS = 'x193iq5w xeuugli x13faqbe x1vvkbs x10flsy6 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x41vudc x6prxxf xvq8zen xo1l8bm xzsf02u'
SEE_MORE_TEXT = 'See more'
CLOSE_BUTTON_LABEL = 'Close'

# ============================================================================
# OUTPUT SETTINGS
# ============================================================================
OUTPUT_FILE = 'facebook_marketplace_listings.csv'
PROGRESS_FILE = 'fb_scraper_progress.json'
SESSION_DIR = 'sessions/facebook_marketplace'

# Required fields for validation
REQUIRED_KEYS = ['title', 'price', 'location', 'listing_url']

# ============================================================================
# BROWSER SETTINGS
# ============================================================================
HEADLESS = False  # Set to True for headless mode (no visible browser)
BROWSER_TIMEOUT = 60000  # milliseconds
NAVIGATION_TIMEOUT = 30000  # milliseconds

# ============================================================================
# RETRY SETTINGS
# ============================================================================
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
EXPONENTIAL_BACKOFF = True
