"""
Facebook Marketplace scraper utilities using Playwright and BeautifulSoup.
Handles scraping listings from Facebook Marketplace with login support.
"""

import time
import random
import re
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
import config_facebook_marketplace as config
from models.facebook_marketplace_listing import FacebookMarketplaceListing


def random_delay(min_seconds: float = 2.0, max_seconds: float = 5.0) -> None:
    """
    Add a random delay to mimic human behavior and avoid bot detection.

    Args:
        min_seconds: Minimum delay in seconds
        max_seconds: Maximum delay in seconds
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def create_browser_context(headless: bool = False) -> Tuple[Browser, BrowserContext, Page]:
    """
    Create and configure a Playwright browser context with anti-detection measures.

    Args:
        headless: Whether to run browser in headless mode

    Returns:
        Tuple of (browser, context, page)
    """
    playwright = sync_playwright().start()

    # Launch browser with additional arguments to avoid detection
    browser = playwright.chromium.launch(
        headless=headless,
        args=[
            '--disable-blink-features=AutomationControlled',  # Hide automation
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process'
        ]
    )

    # Randomize viewport size slightly to avoid fingerprinting
    viewport_width = random.randint(1366, 1920)
    viewport_height = random.randint(768, 1080)

    # Create context with realistic browser settings
    context = browser.new_context(
        viewport={'width': viewport_width, 'height': viewport_height},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        locale='en-US',
        timezone_id='America/New_York',
        permissions=['geolocation'],  # Grant permissions like a real user
        color_scheme='light',
        device_scale_factor=1
    )

    page = context.new_page()
    page.set_default_timeout(config.BROWSER_TIMEOUT)
    page.set_default_navigation_timeout(config.NAVIGATION_TIMEOUT)

    # Add script to hide webdriver property
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    return browser, context, page


def login_to_facebook(page: Page, email: str = None, password: str = None) -> bool:
    """
    Login to Facebook using provided credentials.

    Args:
        page: Playwright page object
        email: Facebook email (defaults to config.FB_EMAIL)
        password: Facebook password (defaults to config.FB_PASSWORD)

    Returns:
        True if login successful, False otherwise
    """
    email = email or config.FB_EMAIL
    password = password or config.FB_PASSWORD

    if not email or not password:
        print("Warning: Facebook credentials not provided. Attempting to access without login...")
        return False

    try:
        print(f"Logging in to Facebook as {email}...")
        page.goto(config.FB_LOGIN_URL)
        random_delay(2.0, 4.0)  # Random delay after page load

        # Fill email with human-like typing
        email_input = page.wait_for_selector('input[name="email"]', timeout=10000)
        email_input.fill(email)
        random_delay(0.5, 1.5)  # Random delay after email input

        # Fill password with human-like typing
        password_input = page.wait_for_selector('input[name="pass"]', timeout=10000)
        password_input.fill(password)
        random_delay(0.8, 2.0)  # Random delay before clicking login

        # Click login button
        login_button = page.wait_for_selector('button[name="login"]', timeout=10000)
        login_button.click()

        random_delay(4.0, 7.0)  # Longer random delay after login attempt

        # Check if login was successful
        if "login" in page.url.lower():
            print("Login failed. Please check your credentials.")
            return False

        print("Successfully logged in to Facebook!")
        return True

    except Exception as e:
        print(f"Error during Facebook login: {e}")
        return False


def build_marketplace_url(
    city: str,
    category: str = 'vehicles',
    query: str = '',
    max_price: int = None,
    min_price: int = None,
    min_year: int = None,
    max_year: int = None,
    min_mileage: int = None,
    max_mileage: int = None,
    transmission: str = '',
    make: str = '',
    model: str = '',
    radius: int = None,
    sort_by: str = None
) -> str:
    """
    Build Facebook Marketplace URL with search parameters.

    Args:
        city: City name or city code
        category: Marketplace category ('vehicles', 'search', etc.)
        query: Search query string
        max_price: Maximum price filter
        min_price: Minimum price filter
        min_year: Minimum year (vehicles)
        max_year: Maximum year (vehicles)
        min_mileage: Minimum mileage (vehicles)
        max_mileage: Maximum mileage (vehicles)
        transmission: Transmission type
        make: Vehicle make
        model: Vehicle model
        radius: Search radius in miles
        sort_by: Sort order

    Returns:
        Complete Facebook Marketplace URL
    """
    # Get city code
    city_code = config.CITIES.get(city, city.lower())

    # Base URL
    if category == 'vehicles':
        url = f"{config.FB_MARKETPLACE_BASE}/{city_code}/vehicles"
    elif category == 'search' or query:
        url = f"{config.FB_MARKETPLACE_BASE}/{city_code}/search"
    else:
        url = f"{config.FB_MARKETPLACE_BASE}/{city_code}/{category}"

    # Build query parameters
    params = []

    if query:
        params.append(f"query={query}")

    if max_price is not None:
        params.append(f"maxPrice={max_price}")

    if min_price is not None:
        params.append(f"minPrice={min_price}")

    if category == 'vehicles':
        if min_year:
            params.append(f"minYear={min_year}")
        if max_year:
            params.append(f"maxYear={max_year}")
        if min_mileage is not None:
            params.append(f"minMileage={min_mileage}")
        if max_mileage is not None:
            params.append(f"maxMileage={max_mileage}")
        if transmission:
            params.append(f"transmissionType={transmission}")
        if make:
            params.append(f"make={make}")
        if model:
            params.append(f"model={model}")

    if radius:
        params.append(f"radius={radius}")

    if sort_by:
        params.append(f"sortBy={sort_by}")

    # Combine URL and parameters
    if params:
        url += "?" + "&".join(params)

    return url


def close_popup_dialogs(page: Page) -> None:
    """
    Close any popup dialogs that may appear (login prompts, notifications, etc.).

    Args:
        page: Playwright page object
    """
    try:
        # Try to close any dialog with "Close" button
        close_buttons = page.query_selector_all(f'div[aria-label="{config.CLOSE_BUTTON_LABEL}"]')
        for button in close_buttons:
            try:
                button.click()
                random_delay(0.3, 0.8)  # Random delay after closing popup
            except:
                pass
    except:
        pass


def scroll_page(page: Page, num_scrolls: int = None) -> None:
    """
    Scroll the page to load more listings (infinite scroll) with random human-like delays.

    Args:
        page: Playwright page object
        num_scrolls: Number of times to scroll (defaults to config.MAX_SCROLLS)
    """
    num_scrolls = num_scrolls or config.MAX_SCROLLS

    for i in range(num_scrolls):
        page.keyboard.press('End')
        # Variable delay between scrolls (1.5 to 4 seconds)
        random_delay(1.5, 4.0)
        print(f"  Scrolled {i + 1}/{num_scrolls} times...")


def extract_listings_from_search_page(page: Page, scroll: bool = True) -> List[Dict]:
    """
    Extract listing data from a Facebook Marketplace search results page.

    Args:
        page: Playwright page object
        scroll: Whether to scroll to load more listings

    Returns:
        List of dictionaries containing listing data
    """
    # Close any popups
    close_popup_dialogs(page)
    random_delay(0.5, 1.5)  # Random delay after closing popups

    # Scroll to load more listings
    if scroll:
        scroll_page(page)

    # Wait for listings to load with random delay
    random_delay(2.0, 4.0)

    # Get page HTML
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')

    # Find all listing containers
    listings = soup.find_all('div', class_=config.LISTING_CONTAINER_CLASS)

    print(f"  Found {len(listings)} listings on page")

    parsed_listings = []

    for idx, listing in enumerate(listings):
        try:
            listing_data = {}

            # Extract image
            try:
                image_elem = listing.find('img', class_=config.IMAGE_CLASS)
                listing_data['image_url'] = image_elem.get('src', '') if image_elem else ''
            except:
                listing_data['image_url'] = ''

            # Extract title
            try:
                title_elem = listing.find('span', class_=config.TITLE_CLASS)
                listing_data['title'] = title_elem.get_text(strip=True) if title_elem else ''
            except:
                listing_data['title'] = ''

            # Extract price
            try:
                price_elem = listing.find('span', class_=config.PRICE_CLASS)
                listing_data['price'] = price_elem.get_text(strip=True) if price_elem else ''
            except:
                listing_data['price'] = ''

            # Extract listing URL
            try:
                link_elem = listing.find('a', class_=config.LINK_CLASS)
                relative_url = link_elem.get('href', '') if link_elem else ''
                listing_data['listing_url'] = f"https://www.facebook.com{relative_url}" if relative_url else ''
            except:
                listing_data['listing_url'] = ''

            # Extract location and mileage
            try:
                location_elements = listing.find_all('span', class_=config.LOCATION_MILEAGE_CLASS)
                if location_elements:
                    listing_data['location'] = location_elements[0].get_text(strip=True)
                    if len(location_elements) > 1:
                        mileage_text = location_elements[1].get_text(strip=True)
                        listing_data['mileage'] = mileage_text
                    else:
                        listing_data['mileage'] = ''
                else:
                    listing_data['location'] = ''
                    listing_data['mileage'] = ''
            except:
                listing_data['location'] = ''
                listing_data['mileage'] = ''

            # Only add if we have minimum required fields
            if listing_data.get('title') and listing_data.get('price') and listing_data.get('listing_url'):
                parsed_listings.append(listing_data)
            else:
                print(f"  Skipping listing {idx + 1}: Missing required fields")

        except Exception as e:
            print(f"  Error parsing listing {idx + 1}: {e}")
            continue

    return parsed_listings


def extract_listing_details(page: Page, browser: Browser, listing_url: str) -> Dict:
    """
    Extract detailed information from a specific listing page.

    Args:
        page: Playwright page object
        browser: Browser instance for creating new pages
        listing_url: URL of the listing to extract details from

    Returns:
        Dictionary containing detailed listing information
    """
    details = {}

    # Create new page for the listing
    new_page = browser.new_page()

    try:
        # Navigate to listing
        new_page.goto(listing_url, timeout=30000)
        random_delay(2.5, 5.0)  # Random delay after page load

        # Close any popups
        try:
            close_button = new_page.query_selector(f'div[aria-label="{config.CLOSE_BUTTON_LABEL}"]')
            if close_button:
                close_button.click()
                random_delay(0.8, 1.8)  # Random delay after closing popup
        except:
            pass

        # Click "See more" to expand description
        try:
            see_more_buttons = new_page.query_selector_all(f'span:has-text("{config.SEE_MORE_TEXT}")')
            if see_more_buttons:
                see_more_buttons[-1].click()
                random_delay(1.5, 3.0)  # Random delay after expanding description
        except:
            pass

        # Get page HTML
        html = new_page.content()
        soup = BeautifulSoup(html, 'html.parser')

        # Extract description
        try:
            description_elements = soup.find_all('span', class_=config.DESCRIPTION_CLASS)
            if description_elements:
                # Find the longest text element (usually the description)
                descriptions = [elem.get_text(strip=True) for elem in description_elements]
                description = max(descriptions, key=len)
                details['description'] = description.replace(' See less', '')
            else:
                details['description'] = ''
        except:
            details['description'] = ''

        # Extract transmission type (for vehicles)
        try:
            for elem in soup.find_all('span', class_=config.DESCRIPTION_CLASS):
                text = elem.get_text(strip=True).lower()
                if 'transmission' in text:
                    details['transmission'] = elem.get_text(strip=True)
                    break
            else:
                details['transmission'] = ''
        except:
            details['transmission'] = ''

    except Exception as e:
        print(f"  Error extracting details from {listing_url}: {e}")

    finally:
        new_page.close()

    return details


def scrape_facebook_marketplace(
    city: str = None,
    category: str = None,
    max_pages: int = 1,
    **search_params
) -> List[FacebookMarketplaceListing]:
    """
    Main function to scrape Facebook Marketplace listings.

    Args:
        city: City to search in
        category: Category to search
        max_pages: Maximum number of pages to scrape
        **search_params: Additional search parameters (price, year, make, etc.)

    Returns:
        List of FacebookMarketplaceListing objects
    """
    city = city or config.DEFAULT_CITY
    category = category or config.DEFAULT_CATEGORY

    print(f"\n{'='*80}")
    print(f"FACEBOOK MARKETPLACE SCRAPER")
    print(f"{'='*80}")
    print(f"City: {city}")
    print(f"Category: {category}")
    print(f"Max Pages: {max_pages}")
    print(f"{'='*80}\n")

    all_listings = []

    # Create browser
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
        marketplace_url = build_marketplace_url(city, category, **search_params)
        print(f"\nNavigating to: {marketplace_url}\n")

        # Navigate to marketplace
        page.goto(marketplace_url)
        random_delay(3.0, 6.0)  # Random delay after initial page load

        # Scrape pages
        for page_num in range(1, max_pages + 1):
            print(f"\nScraping page {page_num}/{max_pages}...")

            # Extract listings from current page
            listings = extract_listings_from_search_page(page, scroll=True)

            print(f"  Extracted {len(listings)} listings from page {page_num}")

            all_listings.extend(listings)

            # If fewer listings than expected, we might be at the end
            if len(listings) < config.EXPECTED_LISTINGS_PER_PAGE / 2:
                print(f"  Reached end of listings (found only {len(listings)} listings)")
                break

            # Scroll to load next page (infinite scroll) with generous delay
            if page_num < max_pages:
                print(f"  Loading next page...")
                scroll_page(page, num_scrolls=config.MAX_SCROLLS)
                # Generous random delay between pages (3-8 seconds)
                random_delay(3.0, 8.0)

    except Exception as e:
        print(f"\nError during scraping: {e}")

    finally:
        browser.close()
        playwright.stop()

    print(f"\n{'='*80}")
    print(f"SCRAPING COMPLETE")
    print(f"Total listings extracted: {len(all_listings)}")
    print(f"{'='*80}\n")

    # Convert to Pydantic models
    validated_listings = []
    for listing in all_listings:
        try:
            validated_listings.append(FacebookMarketplaceListing(**listing))
        except Exception as e:
            print(f"Validation error for listing: {e}")

    return validated_listings
