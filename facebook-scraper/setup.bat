@echo off
echo Setting up Deep Seek Web Crawler environment...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not found in PATH.
    echo Please install Python 3.12 or later and add it to your PATH.
    echo You can download Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python found!
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
)

echo Virtual environment created successfully!
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

echo Virtual environment activated!
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
echo.
echo Next steps:
echo 1. Copy ENV_TEMPLATE.txt to .env and add your GROQ_API_KEY
echo 2. Activate the virtual environment with: venv\Scripts\activate.bat
echo 3. Run the crawler with: python main.py
echo.
pause

