# Parallel Scraper for Riyasewana

This parallel version of the scraper runs 10 workers simultaneously to dramatically reduce scraping time.

## Overview

- **Total Pages**: 635 pages
- **Workers**: 10 parallel scrapers
- **Distribution**: 
  - 9 workers: 67 pages each (603 pages)
  - 1 worker: 32 pages (remainder)
  - Total: 635 pages

## Performance Benefits

- **Speed**: ~10x faster than sequential scraping
- **Expected Time**: 1.2-2.4 hours (vs 12-24 hours sequential)
- **Cost**: Still $0 (uses direct HTML extraction)

## Usage

### Run the Parallel Scraper

```powershell
cd deepseek-ai-web-crawler-main
venv\Scripts\activate
python riyasewana_main_parallel.py
```

### Configuration

You can adjust the number of workers in `riyasewana_main_parallel.py`:

```python
NUM_WORKERS = 10  # Change this to adjust parallelism
```

## Features

### Thread-Safe CSV Writing
- File locking ensures no data corruption when multiple workers write simultaneously
- Each worker saves data incrementally
- Failed URLs saved to separate files per worker

### Duplicate Detection
- All workers share the same CSV file
- Duplicates are automatically skipped
- Resumable if interrupted

### Error Handling
- Each worker handles errors independently
- Failed URLs saved to `failed_urls_worker_{id}.txt`
- All failed URLs combined into `failed_urls.txt` at the end

### Progress Tracking
- Each worker shows its own progress
- Final summary aggregates all worker statistics
- Real-time updates as workers process pages

## Output

- **CSV File**: `riyasewana_listings.csv` - All extracted listings
- **Failed URLs**: 
  - `failed_urls_worker_1.txt` through `failed_urls_worker_10.txt`
  - `failed_urls.txt` - Combined failed URLs

## Monitoring

Each worker will display:
- Current page being processed
- Number of URLs found
- Number of listings extracted
- Errors encountered
- Progress summary every 10 pages

## Stopping the Scraper

- Press `Ctrl+C` to stop
- Progress is saved incrementally, so you can resume later
- Each worker completes its current batch before stopping

## System Requirements

- Sufficient memory: Each worker uses its own browser instance (~100-200MB each)
- For 10 workers: ~1-2GB RAM recommended
- Network bandwidth: Multiple concurrent connections

## Tips

1. **Start Small**: Test with fewer workers first (e.g., 2-3) to verify everything works
2. **Monitor Resources**: Watch CPU and memory usage
3. **Adjust Delays**: If you get rate-limited, increase `PAGE_DELAY` and `LISTING_DELAY`
4. **Check Output**: Monitor the CSV file to see progress in real-time

## Troubleshooting

### High Memory Usage
- Reduce `NUM_WORKERS` if your system runs out of memory
- Each worker uses a browser instance

### Rate Limiting
- Increase `PAGE_DELAY` and `LISTING_DELAY` in the script
- The website may limit concurrent connections

### Incomplete Data
- Check `failed_urls.txt` for URLs that failed to extract
- You can re-run the scraper (it skips already-processed URLs)

## Comparison: Sequential vs Parallel

| Aspect | Sequential | Parallel (10 workers) |
|--------|-----------|----------------------|
| Time | 12-24 hours | 1.2-2.4 hours |
| CPU Usage | Low | High |
| Memory Usage | Low (~200MB) | High (~1-2GB) |
| Network | Low | High |
| API Costs | $0 | $0 (direct HTML extraction) |

