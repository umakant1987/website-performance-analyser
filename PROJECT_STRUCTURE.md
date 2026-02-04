# Project Structure

Complete directory structure of the Website Performance Analyzer project.

```
website-performance-analyser/
│
├── backend/                              # Python FastAPI backend
│   ├── app/                             # Main application code
│   │   ├── agents/                      # Individual agent implementations
│   │   │   ├── __init__.py             # Agents package init
│   │   │   ├── lighthouse_agent.py      # Lighthouse performance testing
│   │   │   ├── webpagetest_agent.py     # WebPageTest API integration
│   │   │   ├── gtmetrix_agent.py        # GTmetrix API integration
│   │   │   ├── screenshot_agent.py      # Screenshot capture using Playwright
│   │   │   ├── analysis_agent.py        # Metrics aggregation & AI analysis
│   │   │   └── report_agent.py          # PDF report generation
│   │   │
│   │   ├── main.py                      # FastAPI application & endpoints
│   │   ├── config.py                    # Configuration management
│   │   └── langgraph_workflow.py        # LangGraph orchestration
│   │
│   ├── mcp_servers/                     # MCP server implementations (optional)
│   │   ├── README.md                    # MCP architecture guide
│   │   └── example_lighthouse_mcp.py    # Example MCP server
│   │
│   ├── reports/                         # Generated PDF reports (created at runtime)
│   ├── screenshots/                     # Captured screenshots (created at runtime)
│   │
│   ├── requirements.txt                 # Python dependencies
│   ├── .env.example                     # Environment variables template
│   └── .env                            # Environment variables (git-ignored)
│
├── frontend/                            # React TypeScript frontend
│   ├── src/
│   │   ├── pages/                      # Page components
│   │   │   ├── HomePage.tsx            # Main URL input page
│   │   │   └── ResultsPage.tsx         # Results display page
│   │   │
│   │   ├── components/                 # Reusable components
│   │   │   ├── ProgressBar.tsx         # Progress indicator
│   │   │   ├── MetricsCard.tsx         # Metric display card
│   │   │   └── RecommendationsList.tsx # AI recommendations list
│   │   │
│   │   ├── services/                   # API services
│   │   │   └── api.ts                  # API client
│   │   │
│   │   ├── utils/                      # Utility functions
│   │   │
│   │   ├── App.tsx                     # Main app component
│   │   ├── main.tsx                    # React entry point
│   │   └── index.css                   # Global styles
│   │
│   ├── public/                         # Static assets
│   │
│   ├── package.json                    # Node dependencies
│   ├── vite.config.ts                  # Vite configuration
│   ├── tailwind.config.js              # Tailwind CSS config
│   ├── tsconfig.json                   # TypeScript config
│   ├── index.html                      # HTML entry point
│   ├── .env.example                    # Frontend env template
│   └── .env                           # Frontend env (git-ignored)
│
├── docs/                               # Additional documentation (optional)
│
├── .gitignore                          # Git ignore rules
├── README.md                           # Main documentation
├── QUICK_START.md                      # Quick start guide
├── ARCHITECTURE.md                     # Architecture documentation
├── PROJECT_STRUCTURE.md                # This file
│
├── start-backend.sh                    # Backend startup script (Unix)
├── start-backend.bat                   # Backend startup script (Windows)
├── start-frontend.sh                   # Frontend startup script (Unix)
└── start-frontend.bat                  # Frontend startup script (Windows)
```

## File Descriptions

### Backend Files

#### Core Application
- **main.py**: FastAPI application with REST API endpoints, background task management
- **config.py**: Centralized configuration using pydantic-settings
- **langgraph_workflow.py**: LangGraph workflow orchestration with state management

#### Agents (backend/app/agents/)
- **lighthouse_agent.py**: Uses Playwright to capture Core Web Vitals (FCP, LCP, CLS, TTFB)
- **webpagetest_agent.py**: Integrates with WebPageTest API for comprehensive testing
- **gtmetrix_agent.py**: Integrates with GTmetrix API v2.0 for multi-location testing
- **screenshot_agent.py**: Captures screenshots across desktop, tablet, and mobile viewports
- **analysis_agent.py**: Aggregates metrics and generates AI-powered recommendations using LangChain
- **report_agent.py**: Generates professional PDF reports using ReportLab

#### MCP Servers (backend/mcp_servers/)
- **README.md**: Documentation on MCP architecture and implementation
- **example_lighthouse_mcp.py**: Reference implementation of MCP server for Lighthouse

#### Configuration
- **requirements.txt**: All Python dependencies with versions
- **.env.example**: Template for environment variables with all required keys
- **.env**: Actual environment variables (not tracked in git)

### Frontend Files

#### Pages (frontend/src/pages/)
- **HomePage.tsx**: Main landing page with URL input form and competitor fields
- **ResultsPage.tsx**: Results display with real-time progress, metrics, and recommendations

#### Components (frontend/src/components/)
- **ProgressBar.tsx**: Animated progress bar for analysis status
- **MetricsCard.tsx**: Displays individual performance metrics with color coding
- **RecommendationsList.tsx**: Displays AI-generated recommendations with priority badges

#### Services (frontend/src/services/)
- **api.ts**: Axios-based API client with TypeScript types

#### Configuration
- **package.json**: Node.js dependencies and scripts
- **vite.config.ts**: Vite build tool configuration with proxy setup
- **tailwind.config.js**: Tailwind CSS customization
- **tsconfig.json**: TypeScript compiler options

### Documentation Files

- **README.md**: Complete project documentation, installation guide, and API reference
- **QUICK_START.md**: 5-minute quick start guide for getting up and running
- **ARCHITECTURE.md**: Detailed system architecture, data flow, and design decisions
- **PROJECT_STRUCTURE.md**: This file - complete project structure overview

### Startup Scripts

- **start-backend.sh/bat**: Automated backend setup and startup
- **start-frontend.sh/bat**: Automated frontend setup and startup

## Key Directories (Created at Runtime)

```
backend/
├── reports/              # PDF reports for each analysis
│   └── performance_report_{job_id}_{timestamp}.pdf
│
└── screenshots/          # Screenshots organized by job
    └── {job_id}/
        ├── desktop_{url}.png
        ├── tablet_{url}.png
        ├── mobile_{url}.png
        └── fullpage_{url}.png
```

## Technology Stack by Directory

### Backend
```
backend/
├── FastAPI              # Web framework
├── LangGraph            # Workflow orchestration
├── LangChain            # AI integration
├── Playwright           # Browser automation
├── Pydantic             # Data validation
├── ReportLab            # PDF generation
├── HTTPX/Requests       # HTTP clients
└── Python 3.9+
```

### Frontend
```
frontend/
├── React 18             # UI framework
├── TypeScript           # Type safety
├── Vite                 # Build tool
├── Tailwind CSS         # Styling
├── React Router         # Navigation
├── Axios                # API client
└── Heroicons            # Icons
```

## Import Paths

### Backend
```python
# Main application
from main import app

# Configuration
from config import settings

# Workflow
from langgraph_workflow import create_analysis_graph

# Agents
from agents.lighthouse_agent import LighthouseAgent
from agents.webpagetest_agent import WebPageTestAgent
from agents.gtmetrix_agent import GTMetrixAgent
from agents.screenshot_agent import ScreenshotAgent
from agents.analysis_agent import AnalysisAgent
from agents.report_agent import ReportAgent
```

### Frontend
```typescript
// Pages
import HomePage from './pages/HomePage'
import ResultsPage from './pages/ResultsPage'

// Components
import ProgressBar from './components/ProgressBar'
import MetricsCard from './components/MetricsCard'
import RecommendationsList from './components/RecommendationsList'

// Services
import { performanceApi } from './services/api'
```

## Environment Variables

### Backend (.env)
```env
# AI APIs (at least one required for recommendations)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Performance Testing APIs (optional)
WEBPAGETEST_API_KEY=
GTMETRIX_API_KEY=
GTMETRIX_API_USERNAME=

# Server Configuration
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000

# Storage
REPORTS_DIR=./reports
SCREENSHOTS_DIR=./screenshots
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## Data Flow Through Structure

```
User Request (frontend/src/pages/HomePage.tsx)
    ↓
API Call (frontend/src/services/api.ts)
    ↓
FastAPI Endpoint (backend/app/main.py)
    ↓
Background Task → LangGraph Workflow (backend/app/langgraph_workflow.py)
    ↓
Individual Agents (backend/app/agents/*.py)
    ↓
External APIs (Playwright, WebPageTest, GTmetrix)
    ↓
Results Aggregation (backend/app/agents/analysis_agent.py)
    ↓
PDF Generation (backend/app/agents/report_agent.py)
    ↓
Storage (backend/reports/, backend/screenshots/)
    ↓
API Response (backend/app/main.py)
    ↓
Results Display (frontend/src/pages/ResultsPage.tsx)
```

## Build Artifacts

### Backend
```
backend/
├── __pycache__/         # Python bytecode
├── venv/                # Virtual environment
└── .pytest_cache/       # Test cache
```

### Frontend
```
frontend/
├── node_modules/        # Node packages
├── dist/                # Production build
└── .vite/               # Vite cache
```

All build artifacts are git-ignored.

## Development vs Production

### Development Structure
- In-memory job storage
- Local file storage for reports/screenshots
- Development servers (FastAPI dev, Vite dev)
- Debug logging enabled

### Production Additions
```
website-performance-analyser/
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── kubernetes/
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   └── ingress.yaml
│
└── .github/
    └── workflows/
        ├── backend-ci.yml
        └── frontend-ci.yml
```

## Code Organization Principles

1. **Separation of Concerns**: Each agent handles one responsibility
2. **Modularity**: Components are independent and reusable
3. **Type Safety**: TypeScript frontend, Pydantic backend
4. **Configuration**: Centralized in config.py and .env files
5. **Error Handling**: Multi-level (agent, workflow, API)
6. **Testability**: Each component can be tested independently

## Adding New Features

### Adding a New Agent
1. Create `backend/app/agents/new_agent.py`
2. Implement agent class with `analyze()` method
3. Add to `backend/app/agents/__init__.py`
4. Add node in `backend/app/langgraph_workflow.py`
5. Update state schema if needed

### Adding a New API Endpoint
1. Add route in `backend/app/main.py`
2. Add request/response models
3. Update API client in `frontend/src/services/api.ts`
4. Add TypeScript types

### Adding a New UI Component
1. Create component in `frontend/src/components/`
2. Import in relevant page
3. Add props and types
4. Style with Tailwind CSS

## Conclusion

This project structure is designed for:
- **Clarity**: Easy to navigate and understand
- **Scalability**: Can grow from prototype to production
- **Maintainability**: Clear separation of concerns
- **Developer Experience**: Quick to get started and modify
