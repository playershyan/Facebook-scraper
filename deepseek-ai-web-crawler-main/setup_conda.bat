@echo off
echo Setting up Deep Seek Web Crawler environment using Conda...
echo.

REM Check if Conda is available
conda --version >nul 2>&1
if errorlevel 1 (
    echo Conda is not found in PATH.
    echo Please install Anaconda or Miniconda and add it to your PATH.
    echo You can download from https://www.anaconda.com/products/distribution
    pause
    exit /b 1
)

echo Conda found!
conda --version
echo.

REM Create conda environment
echo Creating conda environment with Python 3.12...
conda create -n deep-seek-crawler python=3.12 -y
if errorlevel 1 (
    echo Failed to create conda environment.
    pause
    exit /b 1
)

echo Conda environment created successfully!
echo.

REM Activate conda environment
echo Activating conda environment...
call conda activate deep-seek-crawler
if errorlevel 1 (
    echo Failed to activate conda environment.
    pause
    exit /b 1
)

echo Conda environment activated!
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
echo 2. Activate the conda environment with: conda activate deep-seek-crawler
echo 3. Run the crawler with: python main.py
echo.
pause

