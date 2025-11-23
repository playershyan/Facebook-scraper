# Setup Instructions

This document provides step-by-step instructions for setting up the Deep Seek Web Crawler project.

## Prerequisites

- Python 3.12 or later installed on your system
- Access to a GROQ API key

## Project Structure

The project is located in: `deepseek-ai-web-crawler-main/deepseek-ai-web-crawler-main/`

## Setup Options

### Option 1: Using venv (Recommended for beginners)

#### Windows:
```bash
cd deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main
setup.bat
```

Or manually:
```bash
cd deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Linux/Mac:
```bash
cd deepseek-ai-web-crawler-main/deepseek-ai-web-crawler-main
chmod +x setup.sh
./setup.sh
```

Or manually:
```bash
cd deepseek-ai-web-crawler-main/deepseek-ai-web-crawler-main
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Option 2: Using Conda (As specified in README)

#### Windows:
```bash
cd deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main
setup_conda.bat
```

Or manually:
```bash
conda create -n deep-seek-crawler python=3.12 -y
conda activate deep-seek-crawler
pip install --upgrade pip
pip install -r requirements.txt
```

## Environment Variables Setup

1. Copy `ENV_TEMPLATE.txt` to `.env`:
   ```bash
   # Windows
   copy ENV_TEMPLATE.txt .env
   
   # Linux/Mac
   cp ENV_TEMPLATE.txt .env
   ```

2. Open `.env` and replace `your_groq_api_key_here` with your actual GROQ API key.

## Running the Crawler

Once setup is complete:

1. Activate the environment:
   - **venv (Windows):** `venv\Scripts\activate`
   - **venv (Linux/Mac):** `source venv/bin/activate`
   - **Conda:** `conda activate deep-seek-crawler`

2. Run the crawler:
   ```bash
   python main.py
   ```

## Dependencies

The project requires the following packages (installed via `requirements.txt`):
- Crawl4AI==0.4.247
- python-dotenv==1.0.1
- pydantic==2.10.6

## Troubleshooting

### Python not found
- Ensure Python 3.12+ is installed and added to your system PATH
- Download Python from: https://www.python.org/downloads/

### Conda not found
- Install Anaconda or Miniconda: https://www.anaconda.com/products/distribution
- Ensure Conda is added to your system PATH

### API Key Issues
- Make sure the `.env` file exists in the project root
- Verify your GROQ API key is correctly set in the `.env` file
- Check that the API key has proper permissions

## Project Overview

This is a web crawler that extracts venue data (wedding reception venues) from The Knot website using:
- Asynchronous web crawling with Crawl4AI
- LLM-powered data extraction
- Data export to CSV format

