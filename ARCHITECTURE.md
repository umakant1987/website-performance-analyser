# Architecture Documentation

## Overview

The Website Performance Analyzer is built using a modern, scalable agentic AI architecture. It combines multiple specialized agents orchestrated by LangGraph to perform comprehensive website performance analysis.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  - URL Input Form                                           │
│  - Real-time Progress Display                               │
│  - Results Visualization                                     │
│  - PDF Download                                             │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST API
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   Backend (FastAPI)                         │
│  - API Endpoints                                            │
│  - Request Validation                                       │
│  - Job Management                                           │
│  - Background Task Processing                               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              LangGraph Workflow Orchestrator                │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Sequential Flow                         │  │
│  │  Initialize → Lighthouse → WebPageTest → GTmetrix  │  │
│  │  → Screenshots → Analysis → Report                   │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  OR                                                         │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Parallel Flow                           │  │
│  │         ┌─→ Lighthouse ─┐                           │  │
│  │  Init ──┼─→ WebPageTest─┼─→ Screenshots            │  │
│  │         └─→ GTmetrix ───┘     ↓                     │  │
│  │                         Analysis → Report            │  │
│  └─────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ├─────────────────────────────────┐
                           │                                 │
            ┌──────────────▼─────────┐      ┌───────────────▼──────────┐
            │   Individual Agents     │      │   External Services      │
            │                         │      │                          │
            │  • Lighthouse Agent     │──────│  • Playwright           │
            │  • WebPageTest Agent    │──────│  • WebPageTest API      │
            │  • GTmetrix Agent       │──────│  • GTmetrix API         │
            │  • Screenshot Agent     │──────│  • Browser Automation   │
            │  • Analysis Agent       │──────│  • OpenAI/Anthropic     │
            │  • Report Agent         │──────│  • ReportLab (PDF)      │
            └─────────────────────────┘      └──────────────────────────┘
```

## Component Details

### 1. Frontend Layer (React + TypeScript + Vite)

**Responsibilities:**
- User interface for URL input
- Real-time progress tracking
- Results visualization
- PDF report download

**Key Components:**
- `HomePage.tsx`: Main form for URL input
- `ResultsPage.tsx`: Results display and analysis
- `ProgressBar.tsx`: Real-time progress indicator
- `MetricsCard.tsx`: Performance metric display
- `RecommendationsList.tsx`: AI recommendations display

**Technology Stack:**
- React 18 with TypeScript
- Vite for fast builds
- Tailwind CSS for styling
- React Router for navigation
- Axios for API communication

### 2. API Layer (FastAPI)

**Responsibilities:**
- REST API endpoints
- Request validation
- Background task management
- Job state management
- Error handling

**Key Endpoints:**
```
POST   /api/analyze       - Start new analysis
GET    /api/status/{id}   - Get analysis status
GET    /api/results/{id}  - Get complete results
GET    /api/download/{id} - Download PDF report
GET    /health            - Health check
DELETE /api/jobs/{id}     - Delete job and cleanup
```

**Data Flow:**
1. Receive analysis request
2. Validate URLs
3. Create unique job ID
4. Start background analysis task
5. Return job ID to client
6. Poll for status updates
7. Return results when complete

### 3. LangGraph Orchestration Layer

**Responsibilities:**
- Workflow orchestration
- Agent coordination
- State management
- Error recovery
- Progress tracking

**State Schema:**
```typescript
interface AnalysisState {
  job_id: string
  main_url: string
  competitor_urls: string[]

  // Results from agents
  lighthouse_results: Array<any>
  webpagetest_results: Array<any>
  gtmetrix_results: Array<any>
  screenshots: Array<any>

  // Aggregated data
  aggregated_metrics: object
  recommendations: Array<string>
  pdf_data: object

  // Status
  status: string
  progress: number
  errors: Array<string>
}
```

**Workflow Patterns:**

#### Sequential Flow
Agents run one after another. Simpler, but slower.
```
Initialize → Lighthouse → WebPageTest → GTmetrix
  → Screenshots → Analysis → Report
```

#### Parallel Flow
Performance tests run simultaneously. Faster, more complex.
```
                  ┌─→ Lighthouse ─┐
Initialize ───────┼─→ WebPageTest ┼─→ Screenshots → Analysis → Report
                  └─→ GTmetrix ───┘
```

### 4. Agent Layer

Each agent is a specialized component responsible for a specific task.

#### Lighthouse Agent
- **Purpose**: Core Web Vitals measurement using Chrome DevTools
- **Technology**: Playwright for browser automation
- **Metrics Collected**:
  - First Contentful Paint (FCP)
  - Largest Contentful Paint (LCP)
  - Cumulative Layout Shift (CLS)
  - Time to First Byte (TTFB)
  - Performance scores
- **Output**: Metrics + suggestions

#### WebPageTest Agent
- **Purpose**: Comprehensive performance testing
- **Technology**: WebPageTest API
- **Metrics Collected**:
  - Load time
  - Speed Index
  - Total Blocking Time
  - Waterfall chart
  - Lighthouse scores
- **Features**:
  - Fallback mode when API key unavailable
  - Polling for async results

#### GTmetrix Agent
- **Purpose**: Multi-location performance testing
- **Technology**: GTmetrix API v2.0
- **Metrics Collected**:
  - Performance score
  - Structure score
  - Page load time
  - Page size
  - Request count
- **Features**:
  - Fallback mode when credentials unavailable
  - Polling for async results

#### Screenshot Agent
- **Purpose**: Visual documentation
- **Technology**: Playwright
- **Captures**:
  - Desktop (1920x1080)
  - Tablet (768x1024)
  - Mobile (375x667)
  - Full page screenshot
- **Output**: Image files + metadata

#### Analysis Agent
- **Purpose**: Metrics aggregation and AI recommendations
- **Technology**: LangChain + OpenAI/Anthropic
- **Functions**:
  - Aggregate metrics from all sources
  - Calculate averages and comparisons
  - Generate AI-powered recommendations
  - Rank against competitors
- **Fallback**: Rule-based recommendations when AI unavailable

#### Report Agent
- **Purpose**: PDF report generation
- **Technology**: ReportLab
- **Sections**:
  - Executive summary
  - Performance scores
  - Detailed metrics
  - Competitor comparison
  - AI recommendations
  - Screenshots
- **Output**: Professional PDF report

## Data Flow

### Complete Analysis Flow

```
1. User submits URL(s)
   ↓
2. FastAPI validates and creates job
   ↓
3. Background task starts LangGraph workflow
   ↓
4. Initialize node sets up state
   ↓
5. Lighthouse agent analyzes URL(s)
   ├─ Uses Playwright to load pages
   ├─ Collects Web Vitals
   └─ Generates suggestions
   ↓
6. WebPageTest agent (if API key available)
   ├─ Submits test to WebPageTest
   ├─ Polls for results
   └─ Parses metrics
   ↓
7. GTmetrix agent (if credentials available)
   ├─ Submits test to GTmetrix
   ├─ Polls for results
   └─ Parses metrics
   ↓
8. Screenshot agent
   ├─ Captures desktop view
   ├─ Captures tablet view
   ├─ Captures mobile view
   └─ Captures full page
   ↓
9. Analysis agent
   ├─ Aggregates all metrics
   ├─ Calculates comparisons
   ├─ Invokes AI for recommendations
   └─ Generates summary
   ↓
10. Report agent
    ├─ Formats all data
    ├─ Generates PDF
    └─ Returns report path
    ↓
11. Results stored in job state
    ↓
12. Frontend polls and displays results
```

## State Management

### Job State Storage

**Development**: In-memory dictionary
```python
jobs: Dict[str, AnalysisState] = {}
```

**Production**: Redis
```python
import redis
redis_client = redis.from_url(settings.redis_url)
```

### State Updates

Each agent updates the shared state:
```python
state['lighthouse_results'].append(result)
state['progress'] = 25
return state
```

LangGraph handles state merging using `operator.add` for lists.

## Error Handling

### Multi-Level Error Handling

1. **Agent Level**: Try/catch within each agent
   - Captures API failures
   - Network timeouts
   - Invalid responses
   - Adds to `state['errors']`

2. **Workflow Level**: Global exception handler
   - Captures workflow failures
   - Sets job status to 'failed'
   - Preserves partial results

3. **API Level**: FastAPI exception handlers
   - Returns appropriate HTTP status codes
   - Provides error messages to frontend

### Graceful Degradation

- WebPageTest failure → Continue with Lighthouse
- GTmetrix failure → Continue with available data
- AI API unavailable → Use rule-based recommendations
- Screenshot failure → Continue without images

## Scalability Considerations

### Current Architecture (Development)
- Single server
- In-memory job storage
- Synchronous background tasks

### Production Scaling Options

1. **Horizontal Scaling**
   - Multiple FastAPI instances behind load balancer
   - Redis for shared job state
   - Distributed task queue (Celery + Redis)

2. **Service Separation**
   - Separate screenshot service
   - Separate report generation service
   - MCP servers for each testing tool

3. **Caching**
   - Cache API responses (WebPageTest, GTmetrix)
   - Cache PDF reports for identical requests
   - CDN for frontend assets

4. **Rate Limiting**
   - Per-IP rate limiting
   - API key-based quotas
   - Queue prioritization

## MCP Server Architecture (Optional)

For production deployments, convert agents to MCP servers:

```
┌─────────────────────────────────────────────────────────┐
│              LangGraph Orchestrator                      │
└───────────────┬─────────────────────────────────────────┘
                │
        ┌───────┴────────┬──────────┬──────────┐
        │                │          │          │
    ┌───▼───┐        ┌──▼──┐   ┌───▼──┐   ┌──▼───┐
    │ Light │        │ WPT │   │ GTM  │   │Screen│
    │house  │        │ MCP │   │ MCP  │   │ MCP  │
    │ MCP   │        │     │   │      │   │      │
    └───────┘        └─────┘   └──────┘   └──────┘
```

**Benefits**:
- Independent scaling
- Language-agnostic
- Reusable across projects
- Better error isolation

## Performance Optimization

### Current Optimizations
- Async/await throughout
- Parallel test execution (optional)
- Playwright connection pooling
- Minimal data serialization

### Future Optimizations
- Result caching (Redis)
- CDN for screenshots
- Streaming results
- Incremental progress updates
- Database indexing
- Connection pooling

## Security Considerations

### Implemented
- CORS configuration
- URL validation
- Request size limits
- Timeout protection

### Production Requirements
- API key authentication
- Rate limiting
- Input sanitization
- HTTPS only
- Secrets management (Vault, AWS Secrets Manager)
- Job cleanup scheduler
- File storage limits

## Monitoring & Observability

### Recommended Tools
- **Logging**: Structured JSON logs
- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry
- **APM**: New Relic / DataDog
- **Error Tracking**: Sentry

### Key Metrics to Monitor
- Request rate
- Analysis completion time
- Agent success rates
- API error rates
- Queue depth
- Resource usage (CPU, Memory, Disk)

## Testing Strategy

### Unit Tests
- Individual agent logic
- Metric calculations
- Score ratings

### Integration Tests
- API endpoints
- LangGraph workflow
- Database operations

### End-to-End Tests
- Complete analysis flow
- PDF generation
- Error scenarios

## Deployment

### Docker Deployment

```dockerfile
# Backend
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium --with-deps
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]

# Frontend
FROM node:18 as build
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: performance-analyzer
spec:
  replicas: 3
  selector:
    matchLabels:
      app: performance-analyzer
  template:
    spec:
      containers:
      - name: backend
        image: performance-analyzer-backend:latest
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: redis-url
```

## Conclusion

This architecture provides:
- **Modularity**: Independent, testable components
- **Scalability**: Can grow from single server to distributed system
- **Maintainability**: Clear separation of concerns
- **Extensibility**: Easy to add new agents or metrics
- **Reliability**: Graceful degradation and error handling
