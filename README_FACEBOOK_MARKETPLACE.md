# Facebook Marketplace Scraper

A powerful, production-ready scraper for extracting listings from Facebook Marketplace using Playwright and BeautifulSoup.

## ⚠️ Disclaimer

**You use this software at your own risk. The authors cannot be held responsible for any potential consequences, including potential bans from Meta/Facebook.**

This tool is for educational and research purposes only. Always comply with Facebook's Terms of Service and robots.txt. Use responsibly and ethically.

## 🌟 Features

- **Multiple Execution Modes**:
  - Sequential scraping for reliability
  - Parallel scraping for speed (5 workers)

- **Advanced Filtering**:
  - City-based searches (40+ major US cities + international)
  - Category filtering (vehicles, property, electronics, general search)
  - Price range filtering
  - Vehicle-specific filters (year, make, model, mileage, transmission)
  - Search radius customization

- **Data Extraction**:
  - Title, price, location
  - Images, listing URLs
  - Vehicle details (mileage, transmission, year, make, model)
  - Seller descriptions
  - Posting dates

- **Robust Architecture**:
  - Pydantic data validation
  - Thread-safe CSV writing
  - Duplicate detection and removal
  - Comprehensive error handling
  - Automatic deduplication

- **Export Formats**:
  - CSV with all fields
  - JSON for programmatic access
  - Statistics and summary reports

## 📋 Prerequisites

- Python 3.8+
- Facebook account (email and password)
- Internet connection

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd Facebook-scraper

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Configuration

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Facebook credentials
FB_EMAIL=your_email@example.com
FB_PASSWORD=your_password
```

**Important**: Never commit your `.env` file with real credentials!

### 3. Test the Scraper

Run a quick test to ensure everything is working:

```bash
python test_facebook_marketplace.py
```

This will scrape one page (~20-30 listings) and verify the setup.

### 4. Run the Scraper

**Sequential Mode** (single-threaded, more stable):
```bash
python facebook_marketplace_main.py
```

**Parallel Mode** (5 workers, faster):
```bash
python facebook_marketplace_main_parallel.py
```

## 📖 Usage

### Basic Usage

The simplest way to use the scraper is to edit the configuration directly in the main scripts:

**facebook_marketplace_main.py** or **facebook_marketplace_main_parallel.py**:

```python
# Customize these parameters
CITY = 'Los Angeles'  # Change to your target city
CATEGORY = 'vehicles'  # 'vehicles', 'search', 'property', etc.
MAX_PAGES = 10  # Number of pages to scrape

search_params = {
    'query': '',  # Search keyword (optional)
    'max_price': 50000,
    'min_price': 0,
    'radius': 50,  # miles
    'sort_by': 'creation_time_descend',
}

# For vehicles
if CATEGORY == 'vehicles':
    search_params.update({
        'min_year': 2010,
        'max_year': 2024,
        'min_mileage': 0,
        'max_mileage': 150000,
        'transmission': 'automatic',  # 'automatic', 'manual', or ''
        'make': 'honda',  # e.g., 'honda', 'toyota', or ''
        'model': 'civic',  # e.g., 'civic', 'camry', or ''
    })
```

### Programmatic Usage

You can also use the scraper programmatically:

```python
from utils.facebook_marketplace_scraper import scrape_facebook_marketplace
from utils.facebook_marketplace_data_utils import save_listings_to_csv

# Scrape listings
listings = scrape_facebook_marketplace(
    city='New York',
    category='vehicles',
    max_pages=5,
    max_price=30000,
    min_price=10000,
    min_year=2018,
    transmission='automatic',
    make='toyota'
)

# Save to CSV
save_listings_to_csv(listings, 'my_listings.csv')

# Access listing data
for listing in listings:
    print(f"{listing.title} - {listing.price}")
    print(f"Location: {listing.location}")
    print(f"URL: {listing.listing_url}")
```

## 🎯 Supported Cities

The scraper supports 40+ major US cities and some international cities:

**United States**:
- New York, Los Angeles, Chicago, Houston, Phoenix, Philadelphia
- San Antonio, San Diego, Dallas, San Jose, Austin, Jacksonville
- Fort Worth, Columbus, Charlotte, San Francisco, Indianapolis
- Seattle, Denver, Washington DC, Boston, El Paso, Nashville
- Detroit, Oklahoma City, Portland, Las Vegas, Memphis, Louisville
- Baltimore, Milwaukee, Albuquerque, Tucson, Fresno, Sacramento
- Kansas City, Atlanta, Miami, Cleveland, New Orleans, Tampa
- Minneapolis, Orlando, Arlington, Cincinnati, Honolulu, Pittsburgh

**International**:
- Brisbane (Australia)

To add more cities, update the `CITIES` dictionary in `config_facebook_marketplace.py`.

## 📊 Output

### CSV Format

The scraper generates a CSV file with the following fields:

- `title` - Listing title
- `price` - Listed price
- `location` - Geographic location
- `image_url` - URL to listing image
- `listing_url` - Direct link to the listing
- `mileage` - Vehicle mileage (if applicable)
- `transmission` - Transmission type (if applicable)
- `year` - Vehicle year (if applicable)
- `make` - Vehicle make (if applicable)
- `model` - Vehicle model (if applicable)
- `description` - Seller's description
- `condition` - Item condition
- `posted_date` - When posted
- `seller_name` - Seller name
- `category` - Marketplace category

### JSON Format

The same data is also exported in JSON format for programmatic access.

## ⚙️ Configuration

All configuration is managed through `config_facebook_marketplace.py`:

### Key Settings

```python
# Authentication
FB_EMAIL = os.getenv('FB_EMAIL', '')
FB_PASSWORD = os.getenv('FB_PASSWORD', '')

# Scraping parameters
DEFAULT_MAX_PAGES = 10
EXPECTED_LISTINGS_PER_PAGE = 30
SCROLL_PAUSE_TIME = 2  # seconds between scrolls
MAX_SCROLLS = 5  # scrolls per page

# Parallel execution
NUM_WORKERS = 5
WORKER_START_DELAY = 3  # seconds between worker starts

# Browser settings
HEADLESS = False  # Set True for headless mode
BROWSER_TIMEOUT = 60000  # milliseconds
```

## 🔧 Advanced Configuration

### Custom CSS Selectors

If Facebook updates their UI, you may need to update CSS selectors in `config_facebook_marketplace.py`:

```python
LISTING_CONTAINER_CLASS = 'x9f619 x78zum5 ...'  # Update if changed
IMAGE_CLASS = 'xt7dq6l xl1xv1r ...'
TITLE_CLASS = 'x1lliihq x6ikm8r ...'
# etc.
```

### Rate Limiting

To avoid being rate-limited or blocked:

1. Use reasonable delays: `SCROLL_PAUSE_TIME = 2`
2. Don't run too many workers: `NUM_WORKERS = 5`
3. Add delays between worker starts: `WORKER_START_DELAY = 3`
4. Run in non-headless mode initially to mimic real users

## 🧪 Testing

### Quick Test (1 page)

```bash
python test_facebook_marketplace.py
```

### Custom Test

Modify `test_facebook_marketplace.py` to test different configurations:

```python
CITY = 'Chicago'
CATEGORY = 'electronics'
MAX_PAGES = 1
search_params = {
    'max_price': 500,
    'query': 'laptop'
}
```

## 🐛 Troubleshooting

### Issue: "No listings found"

**Possible causes**:
1. Invalid Facebook credentials
2. No listings match your search criteria
3. Facebook UI has changed (update CSS selectors)
4. Rate limiting or temporary block

**Solutions**:
- Verify credentials in `.env`
- Broaden search criteria (increase price range, etc.)
- Run in non-headless mode to observe browser behavior
- Wait a few hours and try again

### Issue: "Login failed"

**Solutions**:
- Check email and password in `.env`
- Try logging in manually in a browser
- Facebook may require 2FA - currently not supported
- Use an account without 2FA enabled

### Issue: "Playwright not installed"

**Solution**:
```bash
playwright install chromium
```

### Issue: Extraction errors

If selectors are outdated:

1. Run in non-headless mode: `HEADLESS = False`
2. Inspect Facebook Marketplace HTML
3. Update CSS selectors in `config_facebook_marketplace.py`

## 📈 Performance

### Sequential Mode
- **Speed**: ~2-3 pages/minute
- **Reliability**: High
- **Resource usage**: Low
- **Best for**: Small scraping jobs, testing

### Parallel Mode (5 workers)
- **Speed**: ~8-10 pages/minute
- **Reliability**: Good
- **Resource usage**: Medium
- **Best for**: Large scraping jobs

### Expected Results
- 1 page = ~20-30 listings
- 10 pages = ~200-300 listings
- 100 pages = ~2,000-3,000 listings

## 🔒 Security & Privacy

- **Never** commit your `.env` file with real credentials
- Use a dedicated Facebook account for scraping
- Be aware of Facebook's Terms of Service
- Consider using a VPN if doing large-scale scraping
- Rotate accounts if scraping extensively

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is for educational purposes only. Use responsibly and at your own risk.

## 🙏 Acknowledgments

This implementation was inspired by and references:
- [passivebot/facebook-marketplace-scraper](https://github.com/passivebot/facebook-marketplace-scraper)
- [martin3252/Facebook_Marketplace_Scraper](https://github.com/martin3252/Facebook_Marketplace_Scraper)

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review troubleshooting section above

## 🗺️ Roadmap

Future enhancements:
- [ ] FastAPI REST API endpoint
- [ ] Streamlit GUI dashboard
- [ ] MongoDB database integration
- [ ] Detailed listing page scraping
- [ ] Email alerts for new listings
- [ ] Price tracking over time
- [ ] 2FA authentication support
- [ ] Proxy rotation support
- [ ] Docker containerization

---

**Happy Scraping! 🚀**

Remember: Use responsibly and ethically. Respect Facebook's Terms of Service.
