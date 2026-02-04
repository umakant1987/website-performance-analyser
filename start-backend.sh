#!/bin/bash

echo "🚀 Starting Website Performance Analyzer Backend..."

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers if not already installed
echo "🎭 Installing Playwright browsers..."
playwright install chromium

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from example..."
    cp .env.example .env
    echo "⚙️  Please edit backend/.env with your API keys"
fi

# Start the server
echo "✅ Starting FastAPI server..."
cd app
python main.py
