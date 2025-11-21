"""
Test script for riyasewana.com scraper
Use this to verify selectors and test extraction before running the full scrape.
"""
import asyncio
import json
import os
import sys
from bs4 import BeautifulSoup

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from dotenv import load_dotenv

from config_riyasewana import BASE_URL
from utils.riyasewana_scraper import get_browser_config, get_llm_strategy, extract_listing_details

load_dotenv()


async def test_search_page():
    """Test extracting listing URLs from a search page."""
    print("=" * 60)
    print("Testing Search Page URL Extraction")
    print("=" * 60)
    
    browser_config = get_browser_config(headless=False)  # Show browser for debugging
    session_id = "test_session"
    
    test_url = f"{BASE_URL}?page=1"
    print(f"\nTesting URL: {test_url}\n")
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=test_url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                session_id=session_id,
            ),
        )
        
        if not result.success:
            print(f"[ERROR] Error fetching page: {result.error_message}")
            return
        
        print(f"[OK] Page loaded successfully\n")
        
        # Parse HTML
        soup = BeautifulSoup(result.cleaned_html, 'html.parser')
        
        # Try different selectors
        selectors = [
            "a[href*='/buy/']",
            "a[href*='/ad/']",
            "a[href*='/listing/']",
            ".listing-link",
            ".ad-link",
            ".item-link",
        ]
        
        print("Testing CSS selectors:")
        print("-" * 60)
        
        found_urls = []
        for selector in selectors:
            links = soup.select(selector)
            urls = []
            for link in links:
                href = link.get('href', '')
                if href and '/buy/' in href:
                    if href.startswith('/'):
                        url = f"https://riyasewana.com{href}"
                    elif href.startswith('http'):
                        url = href
                    else:
                        url = f"https://riyasewana.com/{href}"
                    if url not in urls:
                        urls.append(url)
            
            print(f"{selector:30} → Found {len(urls)} URLs")
            if urls and not found_urls:
                found_urls = urls[:5]  # Store first 5 for display
        
        # Also try finding all links with /buy/ in href
        print("\n" + "-" * 60)
        print("Finding all links containing '/buy/' in href:")
        all_buy_links = soup.find_all('a', href=True)
        buy_urls = []
        for link in all_buy_links:
            href = link.get('href', '')
            if '/buy/' in href:
                if href.startswith('/'):
                    url = f"https://riyasewana.com{href}"
                elif href.startswith('http'):
                    url = href
                else:
                    url = f"https://riyasewana.com/{href}"
                if url not in buy_urls:
                    buy_urls.append(url)
        
        print(f"Total unique /buy/ URLs found: {len(buy_urls)}")
        
        if buy_urls:
            print(f"\nFirst 5 URLs found:")
            for i, url in enumerate(buy_urls[:5], 1):
                print(f"  {i}. {url}")
            
            print(f"\n[SUCCESS] Found {len(buy_urls)} listing URLs on page 1")
            print(f"\nExample URL to test: {buy_urls[0]}")
            return buy_urls[0] if buy_urls else None
        else:
            print("\n[ERROR] No /buy/ URLs found!")
            print("\nTry inspecting the HTML structure manually.")
            print(f"HTML sample (first 2000 chars):")
            print(result.cleaned_html[:2000])
            return None


async def test_listing_page(listing_url: str):
    """Test extracting details from a single listing page."""
    print("\n" + "=" * 60)
    print("Testing Listing Detail Extraction")
    print("=" * 60)
    
    if not os.getenv("GROQ_API_KEY"):
        print("[ERROR] GROQ_API_KEY not found in environment variables!")
        print("Please create a .env file with your GROQ_API_KEY.")
        return
    
    browser_config = get_browser_config(headless=False)  # Show browser for debugging
    llm_strategy = get_llm_strategy()
    session_id = "test_listing_session"
    
    print(f"\nTesting URL: {listing_url}\n")
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=listing_url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=llm_strategy,
                session_id=session_id,
            ),
        )
        
        if not result.success:
            print(f"[ERROR] Error fetching listing: {result.error_message}")
            return
        
        print(f"[OK] Listing page loaded successfully\n")
        
        if not result.extracted_content:
            print("[ERROR] No extracted content from LLM")
            print("\nHTML sample (first 2000 chars):")
            print(result.cleaned_html[:2000])
            return
        
        try:
            extracted_data = json.loads(result.extracted_content)
            
            if isinstance(extracted_data, list) and len(extracted_data) > 0:
                listing_data = extracted_data[0]
            elif isinstance(extracted_data, dict):
                listing_data = extracted_data
            else:
                print(f"[ERROR] Unexpected data format: {type(extracted_data)}")
                print(f"Raw content: {result.extracted_content[:500]}")
                return
            
            print("[SUCCESS] Successfully extracted listing data:")
            print("-" * 60)
            for key, value in listing_data.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"{key:20}: {value[:100]}...")
                else:
                    print(f"{key:20}: {value}")
            
            print("-" * 60)
            print("\n[SUCCESS] Test passed! The scraper should work correctly.")
            
            # Show LLM usage
            print("\nLLM Usage Statistics:")
            llm_strategy.show_usage()
            
        except json.JSONDecodeError as e:
            print(f"[ERROR] Error parsing JSON: {e}")
            print(f"\nRaw extracted content:")
            print(result.extracted_content[:500])


async def main():
    """Run tests."""
    print("\n" + "=" * 60)
    print("Riyasewana Scraper Test Script")
    print("=" * 60)
    print("\nThis script tests:")
    print("1. Extracting listing URLs from a search page")
    print("2. Extracting details from a listing page")
    print("\nPress Ctrl+C to cancel")
    print("=" * 60)
    
    try:
        # Test search page
        test_url = await test_search_page()
        
        if test_url:
            # Ask user if they want to test listing page
            print("\n" + "=" * 60)
            print("Would you like to test listing detail extraction?")
            print("This will use your GROQ API and may consume credits.")
            print("=" * 60)
            
            # For automated testing, proceed directly
            # In interactive mode, you could ask for confirmation
            if test_url:
                await test_listing_page(test_url)
        else:
            print("\n⚠ Cannot test listing page - no URLs found on search page")
            
    except KeyboardInterrupt:
        print("\n\n[WARNING] Test interrupted by user")
    except Exception as e:
        print(f"\n\n[ERROR] Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

