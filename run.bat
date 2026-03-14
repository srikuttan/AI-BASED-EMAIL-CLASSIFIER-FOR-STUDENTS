@echo off
cd /d "%~dp0"
echo Starting AI Email Classifier...

:: Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    call venv\Scripts\activate
    echo Installing dependencies...
    pip install -r backend\requirements.txt
) else (
    call venv\Scripts\activate
)

:: Start browser in a few seconds (gives server time to spin up)
:: The /min flag runs this command minimized so it doesn't distract
start /min cmd /c "timeout /t 3 >nul && start http://127.0.0.1:8000"

:: Run the application
echo Starting backend server...
set ENABLE_EMAIL_CLASSIFICATION=true
python -m backend.main

pause
