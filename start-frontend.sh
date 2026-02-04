#!/bin/bash

echo "🎨 Starting Website Performance Analyzer Frontend..."

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the development server
echo "✅ Starting Vite development server..."
npm run dev
