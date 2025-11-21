# Quick Reference - Riyasewana Scraper

## Commands

### Start Scraping
```powershell
python riyasewana_main_robust.py
```

### Resume from Checkpoint
```powershell
python riyasewana_main_robust.py --resume <session_id>
```

### View Session History
```powershell
python utils/session_viewer.py --list
```

### List Resumable Sessions
```powershell
python utils/session_viewer.py --resumable
```

### Start Dashboard
```powershell
python dashboard_server.py
```
Open: http://localhost:5000

### Test Scraper
```powershell
python test_riyasewana.py
```

---

## Files

| File | Purpose |
|------|---------|
| `riyasewana_main_robust.py` | Main scraper (use this) |
| `riyasewana_main_parallel.py` | Parallel scraper (no recovery) |
| `test_riyasewana.py` | Test script |
| `dashboard_server.py` | Dashboard server |
| `utils/session_viewer.py` | View sessions |
| `riyasewana_listings.csv` | Output file |
| `sessions/sessions_history.json` | Session history |
| `sessions/checkpoints/*.json` | Checkpoints |

---

## Configuration

**Edit `config_riyasewana.py`:**
- `TOTAL_PAGES` - Number of pages to scrape
- `BASE_URL` - Target URL

**Edit `dashboard_config.json`:**
- `title` - Dashboard title
- `refresh_interval` - Auto-refresh (ms)

---

## Features

### ✅ Automatic Error Handling
- Network errors → Auto-retry (5x)
- API errors → Wait & retry
- Crashes → Emergency checkpoint saved

### ✅ Checkpoint System
- Saves every 10 pages
- Saves on errors
- Saves on interruption

### ✅ Resume Capability
- Resume from any checkpoint
- Skips already-processed URLs
- No duplicates, no gaps

### ✅ Session Tracking
- All sessions logged
- View anytime (like browser history)
- Error history per session

### ✅ Data Protection
- CSV saves every 5 listings
- Checkpoints every 10 pages
- No data loss

### ✅ Dashboard
- Real-time progress
- Time estimates
- Worker status
- Auto-updates every 2s

---

## Recovery Workflow

1. **Check sessions:**
   ```powershell
   python utils/session_viewer.py --resumable
   ```

2. **Resume:**
   ```powershell
   python riyasewana_main_robust.py --resume <session_id>
   ```

Done.

---

## What Happens On...

| Event | Action |
|-------|--------|
| Network error | Auto-retry 5x, then checkpoint |
| API rate limit | Wait, checkpoint, retry |
| Laptop dies | Emergency checkpoint saved |
| Ctrl+C | Checkpoint saved, clean exit |
| Any error | Logged, checkpoint saved |

---

## Output

- **CSV:** `riyasewana_listings.csv` (auto-saved every 5 listings)
- **Progress:** `scraper_progress.json` (for dashboard)
- **Sessions:** `sessions/` directory
- **Failed URLs:** `failed_urls.txt` (if any)

---

## Quick Troubleshooting

**No sessions found?** → Scraper hasn't run yet

**Can't resume?** → Check session status with `--resumable`

**Dashboard not updating?** → Check `scraper_progress.json` exists

**Port 5000 in use?** → Change port in `dashboard_server.py`

---

## Important Notes

- Use `riyasewana_main_robust.py` for production
- Checkpoints saved in `sessions/checkpoints/`
- Session history in `sessions/sessions_history.json`
- Dashboard updates automatically
- All data saved incrementally

