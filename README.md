# Website Performance Analyzer - AI Powered

A comprehensive website performance analysis tool powered by agentic AI using LangGraph. This application analyzes website performance using multiple industry-standard tools (Lighthouse, WebPageTest, GTmetrix) and provides AI-generated recommendations for improvement.

## Features

- **Multi-Tool Analysis**: Integrates Lighthouse, WebPageTest, and GTmetrix for comprehensive performance testing
- **Agentic AI Architecture**: Built using LangGraph with specialized agents for each testing service
- **Core Web Vitals**: Measures FCP, LCP, CLS, TTFB, and other critical metrics
- **Multi-Device Screenshots**: Captures screenshots across desktop, tablet, and mobile viewports
- **Competitor Comparison**: Compare your website against up to 5 competitors
- **AI-Powered Recommendations**: Get intelligent, actionable performance recommendations
- **PDF Report Generation**: Download comprehensive PDF reports with all findings
- **Real-time Progress Tracking**: Monitor analysis progress with live updates
- **Beautiful UI**: Modern React frontend with Tailwind CSS

## Architecture

### Backend (FastAPI + LangGraph)

```
backend/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configuration management
│   ├── langgraph_workflow.py     # LangGraph orchestration
│   └── agents/                    # Individual agent implementations
│       ├── lighthouse_agent.py    # Lighthouse testing
│       ├── webpagetest_agent.py   # WebPageTest API
│       ├── gtmetrix_agent.py      # GTmetrix API
│       ├── screenshot_agent.py    # Screenshot capture
│       ├── analysis_agent.py      # Metrics aggregation & AI analysis
│       └── report_agent.py        # PDF report generation
├── mcp_servers/                   # MCP server implementations (optional)
├── requirements.txt
└── .env.example
```

### Frontend (React + TypeScript + Vite)

```
frontend/
├── src/
│   ├── pages/
│   │   ├── HomePage.tsx          # URL input form
│   │   └── ResultsPage.tsx       # Results display
│   ├── components/
│   │   ├── ProgressBar.tsx
│   │   ├── MetricsCard.tsx
│   │   └── RecommendationsList.tsx
│   ├── services/
│   │   └── api.ts                # API client
│   └── App.tsx
├── package.json
└── vite.config.ts
```

## Installation

### Prerequisites

- Python 3.9+
- Node.js 18+
- Playwright (for screenshots)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install chromium
```

5. Create `.env` file from example:
```bash
cp .env.example .env
```

6. Configure your API keys in `.env`:
```env
# Required for AI recommendations
OPENAI_API_KEY=your_openai_key
# OR
ANTHROPIC_API_KEY=your_anthropic_key

# Optional (for enhanced testing)
WEBPAGETEST_API_KEY=your_webpagetest_key
GTMETRIX_API_KEY=your_gtmetrix_key
GTMETRIX_API_USERNAME=your_username
```

7. Start the backend server:
```bash
cd app
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file (optional):
```env
VITE_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

### Basic Analysis

1. Open `http://localhost:3000` in your browser
2. Enter your website URL
3. (Optional) Add competitor URLs for comparison
4. Click "Analyze Performance"
5. Wait for the analysis to complete
6. View results and download PDF report

### API Endpoints

#### Start Analysis
```http
POST /api/analyze
Content-Type: application/json

{
  "mainUrl": "https://example.com",
  "competitors": ["https://competitor1.com", "https://competitor2.com"]
}

Response: {
  "job_id": "uuid",
  "status": "queued",
  "progress": 0,
  "current_step": "Initializing analysis"
}
```

#### Get Status
```http
GET /api/status/{job_id}

Response: {
  "job_id": "uuid",
  "status": "running",
  "progress": 45,
  "current_step": "Running Lighthouse analysis"
}
```

#### Get Results
```http
GET /api/results/{job_id}

Response: {
  "job_id": "uuid",
  "main_url": "https://example.com",
  "lighthouse_results": [...],
  "aggregated_metrics": {...},
  "recommendations": [...]
}
```

#### Download PDF Report
```http
GET /api/download/{job_id}

Response: PDF file
```

## Configuration

### API Keys

#### OpenAI/Anthropic (for AI recommendations)
- OpenAI: Get from https://platform.openai.com/api-keys
- Anthropic: Get from https://console.anthropic.com/settings/keys

#### WebPageTest (optional but recommended)
- Free tier available
- Get API key: https://www.webpagetest.org/getkey.php

#### GTmetrix (optional but recommended)
- Free tier available
- Sign up: https://gtmetrix.com/api/

### Environment Variables

See [.env.example](backend/.env.example) for all available configuration options.

## MCP Servers (Optional)

For production deployments, you can use MCP (Model Context Protocol) servers for better scalability:

1. Each performance testing service runs as an independent MCP server
2. Better error isolation and independent scaling
3. Reusable across different projects

See [backend/mcp_servers/README.md](backend/mcp_servers/README.md) for implementation details.

### When to Use MCP

**Use MCP servers** when:
- Building a production system that needs to scale
- Multiple projects need the same functionality
- Services need to run on different infrastructure

**Use direct integration** (current approach) when:
- Building a prototype or MVP
- Simplicity and deployment ease are priorities
- All services can run in a single application

## Performance Metrics Explained

### Core Web Vitals

- **FCP (First Contentful Paint)**: Time until first content is rendered
  - Good: < 1.8s
  - Needs Improvement: 1.8s - 3.0s
  - Poor: > 3.0s

- **LCP (Largest Contentful Paint)**: Time until largest content is rendered
  - Good: < 2.5s
  - Needs Improvement: 2.5s - 4.0s
  - Poor: > 4.0s

- **CLS (Cumulative Layout Shift)**: Visual stability score
  - Good: < 0.1
  - Needs Improvement: 0.1 - 0.25
  - Poor: > 0.25

- **TTFB (Time to First Byte)**: Server response time
  - Good: < 800ms
  - Needs Improvement: 800ms - 1800ms
  - Poor: > 1800ms

## Troubleshooting

### Playwright Installation Issues

If you encounter errors with Playwright:
```bash
playwright install --with-deps chromium
```

### API Key Errors

The application will work without API keys, but with limited functionality:
- Lighthouse: Works without API key (uses Playwright)
- WebPageTest: Falls back to estimated metrics
- GTmetrix: Falls back to estimated metrics
- AI Recommendations: Falls back to rule-based recommendations

### Port Conflicts

If ports 8000 or 3000 are in use:

Backend:
```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

Frontend (in vite.config.ts):
```typescript
server: {
  port: 3001
}
```

## Production Deployment

### Backend

1. Use production WSGI server:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

2. Set up Redis for job storage:
```python
# Replace in-memory jobs dict with Redis
import redis
redis_client = redis.from_url(settings.redis_url)
```

3. Use environment variables for all secrets

### Frontend

1. Build for production:
```bash
npm run build
```

2. Serve static files:
```bash
npm run preview
```

Or use a CDN/static hosting service (Vercel, Netlify, etc.)

## Development

### Adding New Agents

1. Create agent file in `backend/app/agents/`
2. Implement agent class with `analyze()` method
3. Add node to LangGraph workflow in `langgraph_workflow.py`
4. Update edges to include new agent in flow

### Customizing Reports

Modify `backend/app/agents/report_agent.py` to customize PDF report layout, styling, and content.

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and feature requests, please open an issue on GitHub.

## Acknowledgments

- Lighthouse (Google)
- WebPageTest
- GTmetrix
- LangGraph by LangChain
- FastAPI
- React
- Playwright
