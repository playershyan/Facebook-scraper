# Quick Start - Robust Scraper

## Overview

The **robust scraper** includes comprehensive error handling and recovery:
- ✅ Automatic error handling (network, API, technical)
- ✅ Checkpoint system (save progress regularly)
- ✅ Resume capability (continue from where you stopped)
- ✅ Session history (like browser history - accessible anytime)
- ✅ Crash recovery (handles laptop dying, crashes, etc.)

## Start Scraping

```powershell
cd deepseek-ai-web-crawler-main
venv\Scripts\activate
python riyasewana_main_robust.py
```

## If Something Goes Wrong

### 1. Check Session History

```powershell
python utils/session_viewer.py --list
```

### 2. Find Resumable Sessions

```powershell
python utils/session_viewer.py --resumable
```

### 3. Resume from Checkpoint

```powershell
python riyasewana_main_robust.py --resume <session_id>
```

## What Happens During Errors

### Network Error
- ✅ Automatically retries (up to 5 times)
- ✅ Uses exponential backoff (waits longer each time)
- ✅ Saves checkpoint before retrying
- ✅ Continues when network is back

### API Rate Limiting
- ✅ Detects rate limit errors
- ✅ Increases delay significantly
- ✅ Saves checkpoint
- ✅ Retries after delay

### Laptop Dies / Crash
- ✅ Emergency checkpoint saved before exit
- ✅ Session marked as "interrupted"
- ✅ Resume from checkpoint when you restart

### Ctrl+C
- ✅ Catches interrupt signal
- ✅ Saves checkpoint immediately
- ✅ Clean shutdown
- ✅ Can resume later

## Checkpoint System

Checkpoints are saved:
- Every 10 pages (automatic)
- On errors (emergency)
- On interruption (emergency)
- Every 5 listings saved (implicit)

## Data Protection

- CSV saves every 5 listings (very frequent!)
- Checkpoints every 10 pages
- Emergency saves on errors
- **No data loss!**

## Example Recovery

```powershell
# Start scraping
python riyasewana_main_robust.py

# ... after 200 pages, laptop dies ...

# After restart:
python utils/session_viewer.py --resumable
# Shows: session_20241121_143022 - 200 pages processed

# Resume:
python riyasewana_main_robust.py --resume session_20241121_143022

# Continues from page 201 - no duplicates, no data loss!
```

## Files Created

- `sessions/sessions_history.json` - All session history
- `sessions/checkpoints/*.json` - Recovery checkpoints
- `scraper_progress.json` - Progress for dashboard
- `riyasewana_listings.csv` - Output (saved incrementally)

## Key Features

1. **Error Handling**: Automatic retry for recoverable errors
2. **Checkpoints**: Regular saves for recovery
3. **Resume**: Continue from last checkpoint
4. **Session History**: Track all sessions
5. **Data Protection**: Frequent saves prevent data loss

