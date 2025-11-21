# Error Handling & Recovery System

Comprehensive error handling and recovery system for the Riyasewana scraper.

## Features

✅ **Session Tracking** - Like browser history, accessible anytime
✅ **Automatic Checkpoints** - Saves progress regularly
✅ **Resume Capability** - Continue from where you left off
✅ **Error Recovery** - Handles network, API, and technical errors
✅ **Crash Recovery** - Recovers from unexpected crashes (laptop dies, etc.)
✅ **Data Protection** - Frequent saves prevent data loss
✅ **Session History** - Track all scraping sessions

## Error Handling

The scraper handles various error scenarios:

### 1. Network Errors
- Connection timeouts
- DNS resolution failures
- Unreachable hosts
- **Action**: Automatic retry with exponential backoff

### 2. API Errors
- Rate limiting (429)
- Server errors (500, 502, 503)
- API authentication failures
- **Action**: Wait and retry with increased delays

### 3. Technical Errors
- Parse errors (JSON, HTML)
- File I/O errors
- Memory/resource errors
- **Action**: Save checkpoint and retry or skip

### 4. Crashes
- Laptop dies/battery runs out
- Process killed
- System restart
- Ctrl+C interruption
- **Action**: Save emergency checkpoint before exit

## Session Management

### View Session History

```powershell
python utils/session_viewer.py --list
```

### View Resumable Sessions

```powershell
python utils/session_viewer.py --resumable
```

### Get Session Details

```powershell
python utils/session_viewer.py --session <session_id>
```

### Get Resume Instructions

```powershell
python utils/session_viewer.py --resume-instructions <session_id>
```

## Using the Robust Scraper

### Start New Scraping Session

```powershell
python riyasewana_main_robust.py
```

This will:
- Create a new session
- Save checkpoints every 10 pages
- Save data to CSV every 5 listings
- Handle all errors automatically

### Resume from Checkpoint

If the scraper fails or is interrupted:

1. **Find the session ID**:
   ```powershell
   python utils/session_viewer.py --resumable
   ```

2. **Resume the session**:
   ```powershell
   python riyasewana_main_robust.py --resume <session_id>
   ```

The scraper will:
- Load the last checkpoint
- Skip already-processed URLs
- Continue from where it stopped
- No data loss!

## What Happens During Errors

### Network Error
1. Error detected and classified
2. Logged to session history
3. Automatic retry with exponential backoff
4. If all retries fail, checkpoint saved and item skipped

### API Error (Rate Limiting)
1. Detected as API error
2. Longer delay before retry
3. Checkpoint saved after each failed attempt
4. Continues when API is available

### Laptop Dies / Crash
1. Emergency checkpoint saved (via signal handler)
2. Session marked as "interrupted"
3. On restart, can resume from last checkpoint
4. No work is lost!

### Ctrl+C Interruption
1. Signal handler catches interrupt
2. Checkpoint saved immediately
3. Session marked as "interrupted"
4. Can resume later

## Session Storage

Sessions are stored in `sessions/` directory:

```
sessions/
├── sessions_history.json       # All session history
└── checkpoints/
    ├── session_20241121_143022_checkpoint_20241121_143045.json
    └── session_20241121_143022_checkpoint_20241121_144530.json
```

## Checkpoint System

Checkpoints are saved:
- **Every 10 pages** (configurable via `CHECKPOINT_INTERVAL`)
- **On errors** (emergency checkpoint)
- **On interruption** (emergency checkpoint)
- **On batch saves** (implicit checkpoint)

Each checkpoint contains:
- Last processed page number
- All seen URLs (to avoid duplicates)
- Current statistics
- Worker information
- Failed URLs list

## Data Protection

### Frequent Saves
- **CSV saves**: Every 5 listings (very frequent!)
- **Checkpoint saves**: Every 10 pages
- **Emergency saves**: On any error or interruption

### No Data Loss
- All extracted listings saved immediately
- Progress tracked continuously
- URLs marked as processed to avoid re-scraping

## Recovery Scenarios

### Scenario 1: Network Disconnects

1. Network error occurs
2. Error handler retries automatically (up to 3-5 times)
3. If network comes back, continues automatically
4. If network stays down, checkpoint saved and worker pauses
5. Resume when network is back

### Scenario 2: API Rate Limiting

1. API returns 429 (rate limit)
2. Error handler detects API error
3. Increases delay significantly
4. Retries after delay
5. Checkpoint saved after each attempt

### Scenario 3: Laptop Dies

1. Process gets killed
2. Signal handler catches termination
3. Emergency checkpoint saved
4. Session marked as "interrupted"
5. **On restart**: Resume from checkpoint - no work lost!

### Scenario 4: Scraper Process Killed

1. Process termination detected
2. Cleanup code runs (try/finally blocks)
3. Emergency checkpoint saved
4. Can resume later

### Scenario 5: Power Outage / System Restart

1. Last checkpoint is the recovery point
2. On restart, check session history
3. Find interrupted session
4. Resume from last checkpoint
5. All work after checkpoint is skipped (no duplicates)

## Best Practices

1. **Let it run**: The scraper handles errors automatically
2. **Check progress**: Use dashboard to monitor progress
3. **Don't worry about interruptions**: Can always resume
4. **Check session history**: See what happened in past sessions
5. **Resume if needed**: If interrupted, use `--resume` flag

## Example Recovery Workflow

```powershell
# Start scraping
python riyasewana_main_robust.py

# ... laptop dies after 200 pages ...

# After restart, check sessions
python utils/session_viewer.py --resumable

# Output: session_20241121_143022 - 200 pages processed

# Resume from checkpoint
python riyasewana_main_robust.py --resume session_20241121_143022

# Scraper continues from page 201 - no data loss!
```

## Files Created

- `sessions/sessions_history.json` - Complete session history
- `sessions/checkpoints/*.json` - All checkpoints for recovery
- `scraper_progress.json` - Progress tracker data (for dashboard)
- `riyasewana_listings.csv` - Final output (saved incrementally)

## Error Logging

All errors are logged in:
- Session history (`sessions/sessions_history.json`)
- Each session has an `error_history` field
- Errors are classified and categorized
- Context is preserved for debugging

## Summary

✅ **Network errors**: Automatic retry with backoff
✅ **API errors**: Delayed retry with rate limiting
✅ **Technical errors**: Checkpoint saved, item skipped
✅ **Crashes**: Emergency checkpoint saved
✅ **Interruptions**: Clean shutdown with checkpoint
✅ **Resume**: Always possible from last checkpoint
✅ **No data loss**: Frequent saves protect your data

