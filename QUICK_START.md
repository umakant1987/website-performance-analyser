# Quick Start Guide

Get your website performance analyzer up and running in 5 minutes!

## Prerequisites

Make sure you have installed:
- Python 3.9 or higher
- Node.js 18 or higher
- Git (optional)

## Step 1: Get API Keys (Optional but Recommended)

For best results, get these free API keys:

1. **OpenAI or Anthropic** (for AI recommendations)
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/settings/keys

2. **WebPageTest** (optional)
   - Free tier: https://www.webpagetest.org/getkey.php

3. **GTmetrix** (optional)
   - Free tier: https://gtmetrix.com/api/

## Step 2: Backend Setup

### On Windows:

1. Open Command Prompt or PowerShell
2. Navigate to the project directory
3. Run the startup script:
```cmd
start-backend.bat
```

### On Mac/Linux:

1. Open Terminal
2. Navigate to the project directory
3. Make the script executable and run it:
```bash
chmod +x start-backend.sh
./start-backend.sh
```

### Manual Setup (if scripts don't work):

```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
playwright install chromium

# Copy and edit .env file
cp .env.example .env
# Edit .env with your API keys

cd app
python main.py
```

The backend will start on http://localhost:8000

## Step 3: Frontend Setup

### On Windows:

Open a **new** Command Prompt and run:
```cmd
start-frontend.bat
```

### On Mac/Linux:

Open a **new** Terminal and run:
```bash
chmod +x start-frontend.sh
./start-frontend.sh
```

### Manual Setup:

```bash
cd frontend
npm install
npm run dev
```

The frontend will start on http://localhost:3000

## Step 4: Use the Application

1. Open your browser and go to http://localhost:3000
2. Enter your website URL (e.g., https://example.com)
3. (Optional) Add competitor URLs
4. Click "Analyze Performance"
5. Wait for the analysis to complete (2-5 minutes)
6. View results and download PDF report

## Troubleshooting

### Port Already in Use

**Backend (8000):**
Edit `backend/app/config.py` and change:
```python
port: int = 8001  # or any other available port
```

**Frontend (3000):**
Edit `frontend/vite.config.ts` and change:
```typescript
server: {
  port: 3001
}
```

### Playwright Installation Fails

Try:
```bash
playwright install --with-deps chromium
```

### Module Not Found Errors

Make sure you activated the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

Then reinstall:
```bash
pip install -r requirements.txt
```

### Frontend Won't Start

Delete node_modules and reinstall:
```bash
cd frontend
rm -rf node_modules
npm install
```

## Working Without API Keys

The application will work without any API keys, but with reduced functionality:

- ✅ **Lighthouse analysis**: Works fully (uses Playwright)
- ⚠️  **WebPageTest**: Fallback mode (estimated metrics only)
- ⚠️  **GTmetrix**: Fallback mode (estimated metrics only)
- ⚠️  **AI Recommendations**: Rule-based fallback (still helpful!)
- ✅ **Screenshots**: Works fully
- ✅ **PDF Reports**: Works fully

## Configuration

### Backend Configuration

Edit `backend/.env`:

```env
# Required for AI recommendations
OPENAI_API_KEY=sk-...
# OR
ANTHROPIC_API_KEY=sk-ant-...

# Optional (for enhanced testing)
WEBPAGETEST_API_KEY=your_key
GTMETRIX_API_KEY=your_key
GTMETRIX_API_USERNAME=your_username

# Server settings
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000
```

### Frontend Configuration

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
- Explore [backend/mcp_servers/README.md](backend/mcp_servers/README.md) for MCP integration

## Common Use Cases

### Analyze Your Website
```
Main URL: https://yourwebsite.com
Competitors: (leave empty)
```

### Compare Against Competitors
```
Main URL: https://yourwebsite.com
Competitors:
  - https://competitor1.com
  - https://competitor2.com
```

### Test Different Pages
Run separate analyses for:
- Homepage
- Product pages
- Blog posts
- Landing pages

## Performance Tips

- First analysis takes ~3-5 minutes
- Subsequent analyses are faster (cached resources)
- Analyze during off-peak hours for accurate TTFB
- Use competitors sparingly (each adds ~1-2 minutes)

## Need Help?

- Check the [README.md](README.md) for detailed documentation
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Open an issue on GitHub for bugs or feature requests

## What's Analyzed?

### Core Web Vitals
- **FCP**: First Contentful Paint
- **LCP**: Largest Contentful Paint
- **CLS**: Cumulative Layout Shift
- **TTFB**: Time to First Byte

### Performance Metrics
- Load time
- Speed Index
- Total Blocking Time
- Resource count and sizes
- DOM metrics

### Scores
- Lighthouse Performance Score
- Accessibility Score
- Best Practices Score
- SEO Score

### Visual Analysis
- Desktop screenshots
- Tablet screenshots
- Mobile screenshots
- Full page captures

### AI Insights
- Prioritized recommendations
- Expected impact analysis
- Actionable improvement steps

Happy analyzing! 🚀
