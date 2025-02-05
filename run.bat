@echo off
SETLOCAL EnableDelayedExpansion

:: Check if Git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Git is not installed. Please download and install from https://git-scm.com/downloads
    pause
    exit /b 1
)

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please download and install from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Initialize Git repository
echo Initializing Git repository...
git init .

:: Pull from the main branch
echo Pulling from the main branch...
git pull origin main
if %ERRORLEVEL% NEQ 0 (
    echo Failed to pull from the main branch. Please check your repository URL and network connection.
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies. Please check the requirements.txt file.
    pause
    exit /b 1
)

:: Run the Python script
echo Running src.py...
python src.py
if %ERRORLEVEL% NEQ 0 (
    echo Failed to run src.py.
    pause
    exit /b 1
)

echo.
echo Script executed successfully!
pause
