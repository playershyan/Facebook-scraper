# How to Start Dashboard and Scraper

## Windows Commands

### Terminal 1 - Start Dashboard

```powershell
cd D:\deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main
venv\Scripts\activate
python dashboard_server.py
```

**Keep this window open!**

### Terminal 2 - Run Scraper

```powershell
cd D:\deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main
venv\Scripts\activate
python test_1_page.py
```

---

## Linux/Mac Commands

### Terminal 1 - Start Dashboard

```bash
cd /home/user/Web-scraper
source venv/bin/activate
python dashboard_server.py
```

**Keep this window open!**

### Terminal 2 - Run Scraper

```bash
cd /home/user/Web-scraper
source venv/bin/activate
python test_1_page.py
```

---

## Quick Start Scripts (Windows)

### Option 1: Double-click `start_dashboard.bat`

Then in another window:
```powershell
cd D:\deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main
venv\Scripts\activate
python test_1_page.py
```

### Option 2: Use PowerShell Script

```powershell
# Start dashboard (opens new window)
.\start_dashboard.ps1

# Then run test in current window
.\venv\Scripts\activate
python test_1_page.py
```

---

## Access Dashboard

Once dashboard is running, open browser:
```
http://localhost:5000
```

---

## Expected Results

1. **Dashboard window** shows: "Dashboard available at: http://localhost:5000"
2. **Test script** extracts listings and saves to `output/test_output_1_page.csv`
3. **Dashboard** shows real-time progress updates
4. **CSV file** contains extracted listings

---

## Troubleshooting

**Dashboard not starting?**
- Check if Flask is installed: `pip install Flask flask-cors`
- Check if port 5000 is free: `netstat -ano | findstr :5000`
- See `FIX_DASHBOARD.md` for more help

**Test script not running?**
- Make sure virtual environment is activated
- Check if you're in the correct directory
- Make sure `.env` file exists with `GROQ_API_KEY` (optional)

