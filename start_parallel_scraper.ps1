# Start the parallel scraper in a separate window that persists
# This allows you to close Cursor while the scraper continues running

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting Riyasewana Parallel Scraper" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This window will stay open while the scraper runs." -ForegroundColor Yellow
Write-Host "You can close Cursor - the scraper will continue running." -ForegroundColor Yellow
Write-Host ""
Write-Host "To stop the scraper, press Ctrl+C in this window." -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "D:\deepseek-ai-web-crawler-main\deepseek-ai-web-crawler-main"
.\venv\Scripts\Activate.ps1

Write-Host "Scraper Configuration:" -ForegroundColor White
Write-Host "- Pages to scrape: 635" -ForegroundColor White
Write-Host "- Parallel workers: 10" -ForegroundColor White
Write-Host "- Output file: output\riyasewana_listings.csv" -ForegroundColor White
Write-Host ""
Write-Host "Starting scraper..." -ForegroundColor Green
Write-Host ""

python riyasewana_main_parallel.py

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Scraper has finished or been stopped." -ForegroundColor Yellow
Write-Host "Press any key to close this window..." -ForegroundColor White
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

