# Quick Start - Dashboard & Test

## What You Need

- **2 separate terminal/command prompt windows** (or PowerShell windows)
- Or run dashboard in background

## Option 1: Two Windows (Easiest)

### Step 1: Open First Window - Start Dashboard

1. Open PowerShell or Command Prompt
2. Navigate to project:
   ```powershell
   cd D:\deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main
   ```
3. Activate virtual environment:
   ```powershell
   venv\Scripts\activate
   ```
4. Start dashboard:
   ```powershell
   python dashboard_server.py
   ```
5. **Keep this window open!** You should see:
   ```
   Dashboard available at: http://localhost:5000
   ```

### Step 2: Open Second Window - Run Test

1. **Open a NEW PowerShell or Command Prompt window** (don't close the first one!)
2. Navigate to project:
   ```powershell
   cd D:\deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main
   ```
3. Activate virtual environment:
   ```powershell
   venv\Scripts\activate
   ```
4. Run test:
   ```powershell
   python test_1_page.py
   ```

### Step 3: Open Browser

Open your web browser and go to:
```
http://localhost:5000
```

Watch the dashboard update in real-time!

---

## Option 2: One Window (Run Dashboard in Background)

### Step 1: Start Dashboard in Background

```powershell
cd D:\deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main
venv\Scripts\activate
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'D:\deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main'; .\venv\Scripts\activate; python dashboard_server.py"
```

This opens a NEW window with the dashboard running.

### Step 2: Run Test in Current Window

```powershell
cd D:\deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main
venv\Scripts\activate
python test_1_page.py
```

### Step 3: Open Browser

```
http://localhost:5000
```

---

## What is "Terminal 1" and "Terminal 2"?

- **Terminal/Command Prompt/PowerShell** = The black window where you type commands
- **Terminal 1** = First window (runs dashboard)
- **Terminal 2** = Second window (runs test)

You can have multiple terminal windows open at the same time!

---

## Visual Guide

```
┌─────────────────────────┐
│   Window 1: Dashboard   │  ← Keep this open
│   python dashboard...   │
│   Dashboard available...│
└─────────────────────────┘

┌─────────────────────────┐
│   Window 2: Test        │  ← Run test here
│   python test_1_page.py │
│   [Page 1/1] Processing │
└─────────────────────────┘

┌─────────────────────────┐
│   Browser: Dashboard    │  ← Watch progress
│   http://localhost:5000 │
│   Progress: 100%        │
└─────────────────────────┘
```

---

## Results

After running test:
- **CSV file:** `output/test_output_1_page.csv`
- **Dashboard:** http://localhost:5000 (shows progress)

---

## Quick Commands

**Start Dashboard:**
```powershell
cd D:\deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main
venv\Scripts\activate
python dashboard_server.py
```

**Run Test (in another window):**
```powershell
cd D:\deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main
venv\Scripts\activate
python test_1_page.py
```

**Open Dashboard:**
```
http://localhost:5000
```

Done! ✅

