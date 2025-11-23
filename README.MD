# Facebook Marketplace Scraper

A powerful, production-ready web scraper for extracting listings from Facebook Marketplace using Playwright and BeautifulSoup.

## ⚠️ Disclaimer

**You use this software at your own risk. The authors cannot be held responsible for any potential consequences, including potential bans from Meta/Facebook.**

## 🌟 Key Features

### Facebook Marketplace Scraper (NEW!)
- **Multiple execution modes**: Sequential and parallel scraping
- **Advanced filtering**: City, category, price, vehicle specs (year, make, model, mileage)
- **Complete data extraction**: Title, price, location, images, seller info, descriptions
- **Export formats**: CSV and JSON
- **40+ supported cities** across US and international locations
- **Production-ready**: Error handling, deduplication, data validation

### Legacy Scrapers
- Riyasewana car listings scraper (Sri Lankan classifieds)
- Wedding venue scraper (The Knot)
- Asynchronous web crawling using [Crawl4AI](https://pypi.org/project/Crawl4AI/)
- LLM-powered data extraction with Groq API
- Real-time progress monitoring with web dashboard

## 📁 Project Structure

```
.
├── facebook_marketplace_main.py              # Facebook Marketplace scraper (sequential)
├── facebook_marketplace_main_parallel.py     # Facebook Marketplace scraper (parallel, 5 workers)
├── test_facebook_marketplace.py              # Test script for Facebook Marketplace
├── config_facebook_marketplace.py            # Facebook Marketplace configuration
│
├── riyasewana_main.py                        # Riyasewana car listings scraper
├── riyasewana_main_parallel.py               # Parallel version
├── main.py                                   # Wedding venue scraper (legacy)
│
├── models/
│   ├── facebook_marketplace_listing.py       # Facebook Marketplace data model
│   ├── listing.py                            # Riyasewana listing model
│   └── venue.py                              # Wedding venue model
│
├── utils/
│   ├── facebook_marketplace_scraper.py       # Facebook Marketplace scraping utilities
│   ├── facebook_marketplace_data_utils.py    # Data processing for Facebook Marketplace
│   ├── riyasewana_scraper.py                 # Riyasewana scraping utilities
│   ├── progress_tracker.py                   # Real-time progress tracking
│   ├── session_manager.py                    # Session management
│   └── error_handler.py                      # Error handling
│
├── dashboard/                                # Real-time monitoring dashboard
├── requirements.txt                          # Python dependencies
├── .env.example                              # Environment variables template
├── README_FACEBOOK_MARKETPLACE.md            # Detailed Facebook Marketplace docs
└── README.MD                                 # This file
```

## 🚀 Quick Start - Facebook Marketplace Scraper

### 1. Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Facebook credentials
# FB_EMAIL=your_email@example.com
# FB_PASSWORD=your_password
```

### 3. Test the Scraper

```bash
python test_facebook_marketplace.py
```

### 4. Run the Scraper

**Sequential mode** (stable, single-threaded):
```bash
python facebook_marketplace_main.py
```

**Parallel mode** (faster, 5 workers):
```bash
python facebook_marketplace_main_parallel.py
```

### 5. View Results

Results are saved to:
- `facebook_marketplace_listings.csv` - CSV format
- `facebook_marketplace_listings.json` - JSON format

## 📖 Detailed Documentation

For complete Facebook Marketplace scraper documentation, see:
- **[README_FACEBOOK_MARKETPLACE.md](README_FACEBOOK_MARKETPLACE.md)** - Complete guide with all features, configuration, and troubleshooting

## 🎯 Facebook Marketplace Features

### Supported Categories
- **Vehicles** - Cars, trucks, motorcycles with detailed filters
- **Property** - Real estate listings
- **Electronics** - Computers, phones, gadgets
- **General Search** - Search any category

### Advanced Filters
- **Location**: 40+ major US cities + international
- **Price Range**: Min/max price filtering
- **Vehicles**: Year, make, model, mileage, transmission type
- **Radius**: Search within X miles
- **Sort Options**: Date, price ascending/descending

### Data Extracted
- Title, price, location
- Images and listing URLs
- Vehicle specifications (mileage, year, make, model, transmission)
- Seller descriptions and contact info
- Posting dates and condition

## 🔧 Other Scrapers in This Repository

### Riyasewana Car Listings Scraper

Scrapes car listings from riyasewana.com (Sri Lankan classifieds):

```bash
# Sequential
python riyasewana_main.py

# Parallel (10 workers)
python riyasewana_main_parallel.py

# With dashboard
python dashboard_server.py  # In separate terminal
python riyasewana_main_parallel.py
```

### Wedding Venue Scraper (Legacy)

Scrapes wedding venues from The Knot:

```bash
python main.py
```

## ⚙️ Configuration

### Facebook Marketplace

Edit `config_facebook_marketplace.py` to customize:

```python
# Search defaults
DEFAULT_CITY = 'Los Angeles'
DEFAULT_CATEGORY = 'vehicles'
DEFAULT_MAX_PAGES = 10

# Price range
DEFAULT_MAX_PRICE = 50000
DEFAULT_MIN_PRICE = 0

# Vehicle filters
DEFAULT_MIN_YEAR = 2010
DEFAULT_MAX_YEAR = 2024
DEFAULT_TRANSMISSION = 'automatic'

# Performance
NUM_WORKERS = 5  # Parallel execution
SCROLL_PAUSE_TIME = 2  # Seconds between scrolls
```

### Riyasewana & Wedding Venues

- `config_riyasewana.py` - Riyasewana scraper settings
- `config.py` - Wedding venue scraper settings

## 🔒 Security

- **Never commit** your `.env` file with real credentials
- The `.env` file is already in `.gitignore`
- Use dedicated accounts for scraping
- Respect websites' Terms of Service and robots.txt

## 🐛 Troubleshooting

### "No listings found"
- Verify Facebook credentials in `.env`
- Check search parameters (price range, location, etc.)
- Run in non-headless mode: Set `HEADLESS = False` in config

### "Login failed"
- Verify email/password in `.env`
- Facebook 2FA is not currently supported
- Try account without 2FA

### "Playwright not installed"
```bash
playwright install chromium
```

## 📊 Performance

### Facebook Marketplace
- **Sequential**: ~2-3 pages/minute
- **Parallel (5 workers)**: ~8-10 pages/minute
- **1 page** ≈ 20-30 listings

### Riyasewana
- **Sequential**: ~50 pages/hour (~2,200 listings/hour)
- **Parallel (10 workers)**: ~250 pages/hour (~11,000 listings/hour)

## 🙏 Credits

Facebook Marketplace scraper inspired by:
- [passivebot/facebook-marketplace-scraper](https://github.com/passivebot/facebook-marketplace-scraper)
- [martin3252/Facebook_Marketplace_Scraper](https://github.com/martin3252/Facebook_Marketplace_Scraper)

## 📝 License

This project is for educational purposes only. Use responsibly and at your own risk.
