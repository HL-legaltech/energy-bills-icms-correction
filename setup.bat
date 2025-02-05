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

:: Check if wkhtmltopdf is installed
where wkhtmltopdf >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo wkhtmltopdf is not installed. Please download and install from https://wkhtmltopdf.org/downloads.html
    pause
    exit /b 1
)

:: Clone repository
echo Cloning repository...
git clone https://github.com/HL-legaltech/energy-bills-icms-correction
cd energy-bills-icms-correction

:: Create and activate virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

:: Install requirements
echo Installing dependencies...
pip install -r requirements.txt

:: Create input and output directories
mkdir input 2>nul
mkdir output 2>nul

echo.
echo Setup complete! Please follow these steps:
echo 1. Place your PDF files in the 'input' folder
echo 2. Run 'python src.py' to process the files
echo 3. Check the 'output' folder for your reports
echo.
pause