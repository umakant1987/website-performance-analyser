@echo off
echo Starting Website Performance Analyzer Backend...

cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo Installing Playwright browsers...
playwright install chromium

if not exist ".env" (
    echo .env file not found. Creating from example...
    copy .env.example .env
    echo Please edit backend\.env with your API keys
)

echo Starting FastAPI server...
cd app
python main.py
