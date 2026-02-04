@echo off
echo Starting Website Performance Analyzer Frontend...

cd frontend

if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

echo Starting Vite development server...
npm run dev
