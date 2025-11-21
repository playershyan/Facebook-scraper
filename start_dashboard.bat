@echo off
echo ============================================================
echo Starting Dashboard Server
echo ============================================================
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat

echo Starting dashboard server on http://localhost:5000
echo.
echo Keep this window open to run the dashboard!
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

python dashboard_server.py

pause

