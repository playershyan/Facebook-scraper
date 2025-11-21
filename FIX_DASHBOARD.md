# Fix ERR_CONNECTION_REFUSED

## Problem
Dashboard shows `ERR_CONNECTION_REFUSED` - the server isn't running.

## Solution

### Option 1: Use Startup Script (Easiest)

**Double-click:**
```
start_dashboard.bat
```

Or in PowerShell:
```powershell
.\start_dashboard.ps1
```

This will:
- Navigate to correct directory
- Activate virtual environment
- Start dashboard server
- Keep window open

**Then open browser:** http://localhost:5000

---

### Option 2: Manual Start

**Open PowerShell/Command Prompt:**
```powershell
cd D:\deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main
venv\Scripts\activate
python dashboard_server.py
```

**You should see:**
```
============================================================
Riyasewana Scraper Dashboard Server
============================================================
Dashboard available at: http://localhost:5000
============================================================
```

**Keep this window open!**

**Then open browser:** http://localhost:5000

---

### Option 3: Check if Already Running

**Check if port 5000 is in use:**
```powershell
netstat -ano | findstr :5000
```

If something is using port 5000:
- Stop it first
- Or change port in `dashboard_server.py`:
  ```python
  app.run(host='0.0.0.0', port=5001)  # Change to 5001
  ```
- Then access: http://localhost:5001

---

### Option 4: Install Missing Dependencies

**If dashboard won't start:**

```powershell
cd D:\deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main
venv\Scripts\activate
pip install Flask flask-cors
```

---

## Verify Dashboard is Running

**Check:**
1. Window shows "Dashboard available at: http://localhost:5000"
2. No errors in the window
3. Browser can access http://localhost:5000

**If still not working:**
- Check firewall settings
- Try different port (5001, 8000, etc.)
- Check if Python is in PATH

---

## Quick Fix Steps

1. **Stop any existing dashboard:**
   - Close any windows running `dashboard_server.py`

2. **Start dashboard:**
   - Double-click `start_dashboard.bat`
   - OR run `start_dashboard.ps1`

3. **Wait for message:**
   - "Dashboard available at: http://localhost:5000"

4. **Open browser:**
   - Go to http://localhost:5000

5. **Keep dashboard window open!**
   - Don't close it or dashboard stops

---

## Troubleshooting

**Still not working?**

1. Check Python is installed:
   ```powershell
   python --version
   ```

2. Check Flask is installed:
   ```powershell
   python -c "import flask; print('OK')"
   ```

3. Check dashboard folder exists:
   ```powershell
   Test-Path "dashboard\index.html"
   ```

4. Try different port:
   - Edit `dashboard_server.py`
   - Change `port=5000` to `port=5001`
   - Access: http://localhost:5001

