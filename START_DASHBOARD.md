# Quick Start - Dashboard

## Start Dashboard Server

```powershell
cd deepseek-ai-web-crawler-main
venv\Scripts\activate
python dashboard_server.py
```

Dashboard will be available at: **http://localhost:5000**

## Start Scraper (in separate terminal)

```powershell
cd deepseek-ai-web-crawler-main
venv\Scripts\activate
python riyasewana_main_parallel.py
```

## View Dashboard

Open your browser and go to: **http://localhost:5000**

The dashboard will automatically update every 2 seconds showing:
- Overall progress (pages completed/remaining)
- Time estimates (elapsed, remaining, ETA)
- Listings statistics (found, extracted, saved)
- Worker status (individual worker progress)

