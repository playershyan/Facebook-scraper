import json
import os
import re
from typing import List, Set, Tuple
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    LLMExtractionStrategy,
)

from models.listing import Listing


def get_browser_config(headless: bool = True) -> BrowserConfig:
    """
    Returns the browser configuration for the crawler.
    
    Args:
        headless: Whether to run in headless mode (no GUI)
    
    Returns:
        BrowserConfig: The configuration settings for the browser.
    """
    return BrowserConfig(
        browser_type="chromium",
        headless=headless,
        verbose=False,  # Set to True for debugging
    )


def get_llm_strategy() -> LLMExtractionStrategy:
    """
    Returns the configuration for the language model extraction strategy.
    
    Returns:
        LLMExtractionStrategy: The settings for how to extract data using LLM.
    """
    return LLMExtractionStrategy(
        provider="groq/llama-3.3-70b-versatile",  # Updated to current Groq model
        api_token=os.getenv("GROQ_API_KEY"),
        schema=Listing.model_json_schema(),
        extraction_type="schema",
        instruction=(
            "Extract the car listing information including title, posted date, "
            "posted by (seller name/info), and contact information (phone, email, etc.) "
            "from the following content. If contact info is not directly visible, "
            "extract any contact-related text or buttons."
        ),
        input_format="markdown",
        verbose=False,
    )


async def extract_listing_urls_from_page(
    crawler: AsyncWebCrawler,
    page_url: str,
    session_id: str,
    base_url: str = "https://riyasewana.com"
) -> List[str]:
    """
    Extracts listing URLs from a search results page.
    Simple and direct - just gets all /buy/ URLs.

    Args:
        crawler: The web crawler instance
        page_url: URL of the search results page
        session_id: Session identifier
        base_url: Base URL for the website

    Returns:
        List of listing URLs
    """
    print(f"Extracting listing URLs from: {page_url}")

    try:
        result = await crawler.arun(
            url=page_url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                session_id=session_id,
            ),
        )

        # Handle various error cases
        if not result.success:
            error_msg = result.error_message or "Unknown error"

            # Check for 404 or page not found errors
            if '404' in str(error_msg) or 'not found' in error_msg.lower():
                print(f"  Warning: Page does not exist (404): {page_url}")
                return []

            # Check for other HTTP errors
            if '403' in str(error_msg) or 'forbidden' in error_msg.lower():
                print(f"  Warning: Page is forbidden (403): {page_url}")
                return []

            if '500' in str(error_msg) or 'server error' in error_msg.lower():
                print(f"  Warning: Server error (500): {page_url}")
                return []

            print(f"  Warning: Error fetching page: {error_msg}")
            return []

        # Check if HTML content exists
        if not result.cleaned_html or not result.cleaned_html.strip():
            print(f"  Warning: Page returned empty content: {page_url}")
            return []

    except Exception as e:
        print(f"  Warning: Exception while fetching page: {str(e)}")
        return []

    # Parse HTML to extract listing URLs - simple and direct
    try:
        soup = BeautifulSoup(result.cleaned_html, 'html.parser')
        listing_urls = []
        seen_urls = set()

        # Find all links with /buy/ in href
        all_links = soup.find_all('a', href=True)

        for link in all_links:
            try:
                href = link.get('href', '')
                if not href or '/buy/' not in href:
                    continue

                # Convert relative URLs to absolute
                if href.startswith('/'):
                    full_url = urljoin(base_url, href)
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(page_url, href)

                # Skip duplicates
                if full_url in seen_urls:
                    continue

                listing_urls.append(full_url)
                seen_urls.add(full_url)

            except Exception:
                # Skip this link if there's an error
                continue

        print(f"Found {len(listing_urls)} listing URLs")
        return listing_urls

    except Exception as e:
        print(f"  Warning: Error parsing HTML: {str(e)}")
        return []


def extract_listing_details_from_html(html_content: str, listing_url: str) -> dict:
    """
    Extracts listing details directly from HTML using CSS selectors.
    This is much faster and free compared to LLM extraction.
    Includes comprehensive error handling for missing fields.
    
    Args:
        html_content: Raw HTML content of the listing page
        listing_url: URL of the listing page
    
    Returns:
        Dictionary containing listing details or None if extraction failed
    """
    try:
        # Validate input
        if not html_content or not html_content.strip():
            print(f"  Warning: Empty HTML content for {listing_url}")
            return None
        
        # Parse HTML with error handling
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            print(f"  Warning: Error parsing HTML: {str(e)}")
            return None
        
        # Extract title from <h1> with error handling
        title = None
        try:
            title_elem = soup.select_one('h1') if soup else None
            if title_elem:
                title = title_elem.get_text(strip=True) if hasattr(title_elem, 'get_text') else None
        except Exception as e:
            print(f"  Warning: Error extracting title: {str(e)}")
        
        # Extract posted date and posted by from <h2>
        # Format: "Posted by Prasanna on 2025-11-12 11:53 am, Panadura"
        posted_by = None
        posted_date = None
        
        # Try multiple selectors to find posted info
        posted_info_elem = None
        selectors = [
            'h2[style*="text-align:center"]',
            'h2[style*="text-align: center"]',
            'h2',
            '.posted-info',
            '[class*="posted"]',
        ]
        
        for selector in selectors:
            posted_info_elem = soup.select_one(selector)
            if posted_info_elem:
                posted_text = posted_info_elem.get_text(strip=True)
                if 'Posted by' in posted_text or 'posted by' in posted_text.lower():
                    break
                posted_info_elem = None
        
        if posted_info_elem:
            posted_text = posted_info_elem.get_text(strip=True)
            # Parse "Posted by Prasanna on 2025-11-12 11:53 am, Panadura"
            if 'Posted by' in posted_text or 'posted by' in posted_text.lower():
                try:
                    # Find "Posted by" (case insensitive)
                    posted_by_start = posted_text.lower().find('posted by')
                    if posted_by_start != -1:
                        posted_by_start += len('posted by')
                        # Find " on " after "Posted by"
                        on_index = posted_text.find(' on ', posted_by_start)
                        if on_index == -1:
                            on_index = posted_text.find(' On ', posted_by_start)
                        if on_index == -1:
                            on_index = posted_text.find(' ON ', posted_by_start)
                        
                        if on_index != -1:
                            posted_by = posted_text[posted_by_start:on_index].strip()
                            
                            # Extract posted date (between " on " and "," or end)
                            date_start = on_index + len(' on ')
                            date_end = posted_text.find(',', date_start)
                            if date_end == -1:
                                # If no comma, try to find date pattern or end of string
                                date_end = len(posted_text)
                            
                            posted_date = posted_text[date_start:date_end].strip()
                except Exception as e:
                    print(f"  Warning: Could not parse posted info: {e}")
        
        # If still not found, try searching all text for patterns
        if not posted_by or not posted_date:
            all_text = soup.get_text()
            if 'Posted by' in all_text or 'posted by' in all_text.lower():
                # Try to extract from entire page text
                lines = all_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if 'Posted by' in line or 'posted by' in line.lower():
                        if ' on ' in line or ' On ' in line:
                            try:
                                posted_by_start = line.lower().find('posted by') + len('posted by')
                                on_index = line.find(' on ', posted_by_start)
                                if on_index == -1:
                                    on_index = line.find(' On ', posted_by_start)
                                
                                if on_index != -1 and not posted_by:
                                    posted_by = line[posted_by_start:on_index].strip()
                                
                                if on_index != -1 and not posted_date:
                                    date_start = on_index + len(' on ')
                                    date_end = line.find(',', date_start)
                                    if date_end == -1:
                                        date_end = len(line)
                                    posted_date = line[date_start:date_end].strip()
                                
                                if posted_by and posted_date:
                                    break
                            except Exception:
                                pass
        
        # Extract contact info from table
        # Look for the span with class "moreph" in the Contact row
        contact_info = None
        
        # Try multiple selectors for contact table
        contact_rows = soup.select('table.moret tr')
        if not contact_rows:
            # Try alternative table selectors
            contact_rows = soup.select('table tr')
        
        for row in contact_rows:
            cells = row.select('td')
            if len(cells) >= 2:
                # Check if first cell contains "Contact"
                first_cell_text = cells[0].get_text(strip=True).lower()
                if 'contact' in first_cell_text:
                    # Try multiple selectors for contact info
                    contact_span = cells[1].select_one('span.moreph')
                    if not contact_span:
                        contact_span = cells[1].select_one('span[class*="more"]')
                    if not contact_span:
                        contact_span = cells[1].select_one('span')
                    if not contact_span:
                        # Try just the cell text
                        contact_text = cells[1].get_text(strip=True)
                        if contact_text:
                            contact_info = contact_text
                            break
                    
                    if contact_span:
                        contact_info = contact_span.get_text(strip=True)
                        if contact_info:
                            break
        
        # If still not found, try searching all text for phone numbers
        if not contact_info:
            all_text = soup.get_text()
            # Look for phone number patterns (Sri Lankan format: 0XX-XXXXXXX or +94 XX XXXX XXX)
            import re
            phone_patterns = [
                r'0\d{2}[- ]?\d{7}',  # 0XX-XXXXXXX or 0XX XXXXXXX
                r'\+94\s?\d{2}\s?\d{3}\s?\d{4}',  # +94 XX XXX XXXX
                r'\d{10}',  # 10 digits
            ]
            for pattern in phone_patterns:
                matches = re.findall(pattern, all_text)
                if matches:
                    contact_info = matches[0]
                    break
        
        # If direct extraction failed for any field, return None to trigger LLM fallback
        # But don't crash - just log what's missing
        if not all([title, posted_date, posted_by, contact_info]):
            missing = []
            if not title: missing.append('title')
            if not posted_date: missing.append('posted_date')
            if not posted_by: missing.append('posted_by')
            if not contact_info: missing.append('contact_info')
            print(f"  Warning: Direct extraction missing fields: {', '.join(missing)}")
            return None
        
        # Build result dictionary with safe defaults
        try:
            listing_data = {
                'title': title or '',
                'posted_date': posted_date or '',
                'posted_by': posted_by or '',
                'contact_info': contact_info or '',
                'listing_url': listing_url or '',
            }
            
            # Validate that we have at least some data
            if not listing_data['title']:
                print(f"  Warning: No title found for {listing_url}")
                return None
            
            return listing_data
        except Exception as e:
            print(f"  Warning: Error building listing data: {str(e)}")
            return None
        
    except Exception as e:
        print(f"  Warning: Error in direct HTML extraction: {str(e)}")
        return None


async def extract_listing_details(
    crawler: AsyncWebCrawler,
    listing_url: str,
    llm_strategy: LLMExtractionStrategy,
    session_id: str,
    use_llm_fallback: bool = True,
) -> dict:
    """
    Extracts detailed information from a single listing page.
    First tries direct HTML parsing (fast, free), then falls back to LLM if needed.
    Includes comprehensive error handling for non-existent pages and missing fields.
    
    Args:
        crawler: The web crawler instance
        listing_url: URL of the listing page
        llm_strategy: LLM extraction strategy (used as fallback)
        session_id: Session identifier
        use_llm_fallback: Whether to use LLM if direct extraction fails
    
    Returns:
        Dictionary containing listing details or None if extraction failed
    """
    print(f"Extracting details from: {listing_url}")
    
    try:
        # First, try direct HTML extraction (fast and free)
        result = await crawler.arun(
            url=listing_url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                session_id=session_id,
            ),
        )
        
        # Handle various error cases
        if not result.success:
            error_msg = result.error_message or "Unknown error"
            
            # Check for 404 or page not found errors
            if '404' in str(error_msg) or 'not found' in error_msg.lower():
                print(f"  Warning: Listing page does not exist (404): {listing_url}")
                return None
            
            # Check for other HTTP errors
            if '403' in str(error_msg) or 'forbidden' in error_msg.lower():
                print(f"  Warning: Listing page is forbidden (403): {listing_url}")
                return None
            
            if '500' in str(error_msg) or 'server error' in error_msg.lower():
                print(f"  Warning: Server error (500): {listing_url}")
                return None
            
            print(f"  Warning: Error fetching listing: {error_msg}")
            return None
        
        # Check if HTML content exists
        if not result.cleaned_html or not result.cleaned_html.strip():
            print(f"  Warning: Empty HTML content for {listing_url}")
            return None
        
        # Try direct HTML extraction first
        listing_data = extract_listing_details_from_html(result.cleaned_html, listing_url)
        
        if listing_data:
            return listing_data
        
        # If direct extraction failed and LLM fallback is enabled, use LLM
        if use_llm_fallback and llm_strategy:
            print(f"  [LLM] Using LLM fallback...")
            try:
                result_llm = await crawler.arun(
                    url=listing_url,
                    config=CrawlerRunConfig(
                        cache_mode=CacheMode.BYPASS,
                        extraction_strategy=llm_strategy,
                        session_id=session_id,
                    ),
                )
                
                if not result_llm or not result_llm.success:
                    error_msg = result_llm.error_message if result_llm else "Unknown error"
                    
                    # Skip LLM fallback for non-existent pages
                    if '404' in str(error_msg) or 'not found' in str(error_msg).lower():
                        print(f"  Warning: Listing does not exist (404), skipping LLM fallback")
                        return None
                    
                    print(f"  Warning: Error fetching listing with LLM: {error_msg}")
                    return None
                
                if not result_llm.extracted_content:
                    print(f"  Warning: No extracted content from LLM")
                    return None
                
                try:
                    # Parse extracted content
                    import json
                    extracted_data = json.loads(result_llm.extracted_content)
                    
                    # Handle both list and single object responses
                    if isinstance(extracted_data, list) and len(extracted_data) > 0:
                        listing_data = extracted_data[0]
                    elif isinstance(extracted_data, dict):
                        listing_data = extracted_data
                    else:
                        print(f"  Warning: Unexpected extracted data format")
                        return None
                    
                    # Validate required fields (allow partial data)
                    required_fields = ['title', 'posted_date', 'posted_by', 'contact_info']
                    if not all(field in listing_data for field in required_fields):
                        missing = [f for f in required_fields if f not in listing_data]
                        print(f"  Warning: LLM response missing fields: {', '.join(missing)}")
                        # Fill missing fields with empty strings
                        for field in required_fields:
                            if field not in listing_data:
                                listing_data[field] = ''
                    
                    # Ensure listing_url is included
                    listing_data['listing_url'] = listing_url
                    
                    print(f"  [LLM] Successfully extracted via LLM")
                    return listing_data
                    
                except json.JSONDecodeError as e:
                    print(f"  Warning: Error parsing JSON from LLM: {str(e)}")
                    return None
                except Exception as e:
                    print(f"  Warning: Error processing LLM response: {str(e)}")
                    return None
            except Exception as e:
                print(f"  Warning: Error fetching listing with LLM: {str(e)}")
                return None
        
        # Both methods failed
        print(f"  Warning: Could not extract listing details from {listing_url}")
        return None
        
    except Exception as e:
        print(f"  Warning: Unexpected error in extract_listing_details: {str(e)}")
        return None


async def fetch_listing_urls_from_page(
    crawler: AsyncWebCrawler,
    page_number: int,
    base_url: str,
    session_id: str,
) -> List[str]:
    """
    Fetches listing URLs from a specific page number.
    Simple and direct - no filtering.

    Args:
        crawler: The web crawler instance
        page_number: Page number to fetch
        base_url: Base URL for search pages (e.g., https://riyasewana.com/search/cars)
        session_id: Session identifier

    Returns:
        List of listing URLs
    """
    # Construct page URL using the pattern: https://riyasewana.com/search/cars?page=2
    if page_number == 1:
        # Page 1 doesn't need the page parameter
        page_url = base_url
    else:
        # Pages 2+ use ?page=N or &page=N depending on existing query string
        if '?' in base_url:
            page_url = f"{base_url}&page={page_number}"
        else:
            page_url = f"{base_url}?page={page_number}"

    return await extract_listing_urls_from_page(
        crawler,
        page_url,
        session_id,
        base_url="https://riyasewana.com"
    )

