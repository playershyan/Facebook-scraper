# How to Start Dashboard

## Quick Start

### Method 1: Double-Click (Easiest!)

**Just double-click this file:**
```
start_dashboard.bat
```

A window will open with the dashboard running!

**Then open your browser:** http://localhost:5000

**Keep the window open** - if you close it, dashboard stops.

---

### Method 2: PowerShell Script

**Right-click `start_dashboard.ps1` → "Run with PowerShell"**

---

### Method 3: Command Line

**Open PowerShell or Command Prompt:**

```powershell
cd D:\deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main
venv\Scripts\activate
python dashboard_server.py
```

**You'll see:**
```
Dashboard available at: http://localhost:5000
```

**Keep this window open!**

**Then open browser:** http://localhost:5000

---

## Important Notes

1. **Keep the window open** - Dashboard stops if you close the window
2. **Wait for message** - Look for "Dashboard available at: http://localhost:5000"
3. **No errors** - If you see errors, check `FIX_DASHBOARD.md`

---

## What If It Doesn't Work?

**Check `FIX_DASHBOARD.md` for troubleshooting steps.**

Common issues:
- Port 5000 already in use
- Flask not installed
- Dashboard folder missing

