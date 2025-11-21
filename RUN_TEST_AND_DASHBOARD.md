# How to Run Test and Access Dashboard

## What is "Terminal 1" and "Terminal 2"?

**Terminal** = PowerShell or Command Prompt window (the black window where you type commands)

- **Terminal 1** = First window (keep open, runs dashboard)
- **Terminal 2** = Second window (open NEW window, runs test)

You need **2 separate windows** - one for dashboard, one for test.

---

## Quick Steps

### 1. Start Dashboard Server

**Open PowerShell/Command Prompt (Window 1):**
```powershell
cd D:\deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main
venv\Scripts\activate
python dashboard_server.py
```

You should see:
```
============================================================
Riyasewana Scraper Dashboard Server
============================================================
Dashboard available at: http://localhost:5000
API endpoint: http://localhost:5000/api/progress
============================================================
```

### 2. Access Dashboard

**Open your browser and go to:**
```
http://localhost:5000
```

The dashboard will show:
- Real-time progress
- Pages processed
- Listings extracted
- Time estimates
- Worker status

### 3. Run 1-Page Test

**Open a NEW PowerShell/Command Prompt window (Window 2):**
(Don't close Window 1! Keep dashboard running)

```powershell
cd D:\deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main
venv\Scripts\activate
python test_1_page.py
```

This will:
- Scrape 1 page (first 3 listings)
- Save CSV to `output/test_output_1_page.csv`
- Update progress for dashboard
- Create session history

### 4. View Results

**CSV File Location:**
```
output/test_output_1_page.csv
```

**Dashboard:**
- Open http://localhost:5000
- Watch progress in real-time
- Auto-updates every 2 seconds

## Folder Structure

All CSV files are saved in the `output/` folder:

```
output/
├── test_output_1_page.csv
├── test_output_5_pages.csv
└── riyasewana_listings.csv (from full run)
```

## Troubleshooting

### Dashboard Not Accessible?

1. **Check if server is running:**
   ```powershell
   # Look for "Dashboard available at: http://localhost:5000"
   ```

2. **Check port 5000:**
   - Make sure nothing else is using port 5000
   - Change port in `dashboard_server.py` if needed

3. **Check firewall:**
   - Allow Python through Windows Firewall if prompted

### Test Not Running?

1. **Check virtual environment:**
   ```powershell
   venv\Scripts\activate
   ```

2. **Check dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Check .env file:**
   - Make sure `.env` exists with `GROQ_API_KEY` (optional for test)

## Full Workflow

1. **Start dashboard** → Terminal 1
2. **Open browser** → http://localhost:5000
3. **Run test** → Terminal 2: `python test_1_page.py`
4. **Watch progress** → Dashboard updates automatically
5. **Check results** → `output/test_output_1_page.csv`

Done! ✅

