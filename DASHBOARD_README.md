# Dashboard Guide

A real-time web-based dashboard for monitoring the Riyasewana scraper progress.

## Features

✅ **Real-time Progress Tracking**
- Overall progress bar showing completion percentage
- Pages completed vs remaining
- Total work units processed

✅ **Time Estimates**
- Elapsed time
- Estimated remaining time
- Completion time prediction
- Processing rate (work units per minute)

✅ **Listings Statistics**
- URLs found
- Listings extracted
- Listings saved to CSV
- Duplicates skipped
- Failed extractions
- Total errors

✅ **Worker Status**
- Individual worker progress
- Pages processed per worker
- URLs found per worker
- Listings extracted per worker
- Errors per worker

✅ **Future-Proof Configuration**
- Configurable via `dashboard_config.json`
- Compatible with different scraper configurations
- Auto-detects work units and totals

## Setup

### 1. Install Dependencies

```powershell
cd deepseek-ai-web-crawler-main
venv\Scripts\activate
pip install Flask flask-cors
```

### 2. Configure Dashboard (Optional)

Edit `dashboard_config.json` to customize:

```json
{
  "title": "Riyasewana Scraper Dashboard",
  "work_unit": "pages",
  "total_work": 635,
  "expected_items_per_unit": 44,
  "refresh_interval": 2000
}
```

**Configuration Options:**
- `title`: Dashboard title
- `work_unit`: Unit of work (e.g., "pages", "items", "urls")
- `total_work`: Total amount of work to complete
- `expected_items_per_unit`: Expected items per work unit (for estimates)
- `refresh_interval`: Auto-refresh interval in milliseconds (default: 2000)

### 3. Start Dashboard Server

```powershell
python dashboard_server.py
```

The dashboard will be available at: **http://localhost:5000**

### 4. Start Scraper

In a separate terminal:

```powershell
cd deepseek-ai-web-crawler-main
venv\Scripts\activate
python riyasewana_main_parallel.py
```

## Usage

1. **Start Dashboard First**: Run `dashboard_server.py` before starting the scraper
2. **Open Browser**: Navigate to `http://localhost:5000`
3. **Start Scraper**: Run the scraper in a separate terminal
4. **Monitor Progress**: The dashboard updates automatically every 2 seconds

## Dashboard Sections

### Overall Progress
- Visual progress bar with percentage
- Completed vs Remaining vs Total
- Real-time updates

### Time Estimates
- **Elapsed Time**: How long the scraper has been running
- **Remaining Time**: Estimated time to completion (calculated dynamically)
- **Rate**: Work units processed per minute
- **Estimated Completion**: Predicted completion time

### Listings Statistics
- URLs found from search pages
- Successfully extracted listings
- Listings saved to CSV
- Duplicates automatically skipped
- Failed extractions (will be in failed_urls.txt)

### Worker Status
- Status of each parallel worker
- Individual progress per worker
- Pages processed per worker
- Errors per worker

## Progress File

The dashboard reads from `scraper_progress.json` which is automatically created and updated by the scraper.

**File Location**: `scraper_progress.json` (same directory as scraper)

**Update Frequency**: Updated in real-time as the scraper progresses

## Troubleshooting

### Dashboard Shows "Not Started"
- Make sure the scraper is running
- Check that `scraper_progress.json` exists
- Verify file permissions

### Dashboard Not Updating
- Check browser console for errors (F12)
- Verify dashboard server is running
- Check network tab for API calls

### Port Already in Use
- Change port in `dashboard_server.py`:
  ```python
  app.run(host='0.0.0.0', port=5001)  # Change 5000 to another port
  ```

### Configuration Not Loading
- Check `dashboard_config.json` syntax (valid JSON)
- Verify file is in the same directory as `dashboard_server.py`

## Future-Proof Design

The dashboard is designed to work with different scraper configurations:

1. **Automatic Detection**: Reads configuration from `dashboard_config.json`
2. **Flexible Work Units**: Works with "pages", "items", "urls", or any unit
3. **Dynamic Totals**: Adjusts to whatever `total_work` is set
4. **Worker Count**: Automatically displays all active workers
5. **Compatible API**: Progress JSON format is standardized

## Advanced Usage

### Custom Configuration for Different Projects

Create a new `dashboard_config.json`:

```json
{
  "title": "My Custom Scraper",
  "work_unit": "items",
  "total_work": 1000,
  "expected_items_per_unit": 25,
  "refresh_interval": 1000
}
```

The dashboard will automatically adapt to your configuration!

## Notes

- Dashboard server can run independently of scraper
- Progress persists even if dashboard is closed and reopened
- All calculations are done in real-time
- Time estimates improve as more data is collected

