@echo off
REM Start the parallel scraper in a separate window that persists
REM This allows you to close Cursor while the scraper continues running

echo ============================================================
echo Starting Riyasewana Parallel Scraper
echo ============================================================
echo.
echo This window will stay open while the scraper runs.
echo You can close Cursor - the scraper will continue running.
echo.
echo To stop the scraper, press Ctrl+C in this window.
echo.
echo ============================================================
echo.

cd /d "D:\deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main"
call venv\Scripts\activate.bat

echo Scraper Configuration:
echo - Pages to scrape: 635
echo - Parallel workers: 10
echo - Output file: output\riyasewana_listings.csv
echo.
echo Starting scraper...
echo.

python riyasewana_main_parallel.py

echo.
echo ============================================================
echo Scraper has finished or been stopped.
echo Press any key to close this window...
pause >nul

