"""
FastAPI Backend for Website Performance Analysis
Save this file as: backend/app/main.py
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import asyncio
import json
from datetime import datetime
import uuid
import os

from app.langgraph_workflow import create_analysis_graph, AnalysisState
from app.config import settings

app = FastAPI(
    title="Website Performance Analyzer API",
    description="AI-powered website performance analysis using LangGraph and MCP",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class AnalysisRequest(BaseModel):
    mainUrl: HttpUrl
    competitors: Optional[List[HttpUrl]] = []

class AnalysisStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    current_step: str
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# In-memory job storage (use Redis in production)
jobs: Dict[str, AnalysisState] = {}

async def run_analysis(job_id: str, main_url: str, competitor_urls: List[str]):
    """Run the complete analysis workflow"""
    try:
        # Update status to running
        if job_id in jobs:
            jobs[job_id]['status'] = 'running'
            jobs[job_id]['progress'] = 10

        graph = create_analysis_graph()

        # Initialize state for workflow
        initial_state = {
            'job_id': job_id,
            'main_url': main_url,
            'competitor_urls': competitor_urls,
            'aggregated_metrics': {},
            'recommendations': [],
            'pdf_data': {},
            'status': 'running',
            'progress': 10
        }

        # Run the complete workflow
        result = await graph.ainvoke(initial_state)

        # Update job with final results
        if job_id in jobs:
            jobs[job_id]['status'] = result.get('status', 'completed')
            jobs[job_id]['progress'] = result.get('progress', 100)
            jobs[job_id]['lighthouse_results'] = result.get('lighthouse_results', [])
            jobs[job_id]['screenshots'] = result.get('screenshots', [])
            jobs[job_id]['aggregated_metrics'] = result.get('aggregated_metrics', {})
            jobs[job_id]['recommendations'] = result.get('recommendations', [])
            jobs[job_id]['pdf_data'] = result.get('pdf_data', {})
            jobs[job_id]['errors'] = result.get('errors', [])

    except Exception as e:
        print(f"[ERROR] Workflow error: {str(e)}")
        if job_id in jobs:
            jobs[job_id]['status'] = 'failed'
            jobs[job_id]['progress'] = 0
            if 'errors' not in jobs[job_id]:
                jobs[job_id]['errors'] = []
            jobs[job_id]['errors'].append(f"Workflow error: {str(e)}")

@app.post("/api/analyze", response_model=AnalysisStatus)
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start a new performance analysis"""
    job_id = str(uuid.uuid4())

    main_url = str(request.mainUrl)
    competitor_urls = [str(url) for url in request.competitors]

    # Initialize job in storage immediately to avoid race condition
    jobs[job_id] = {
        'job_id': job_id,
        'status': 'queued',
        'progress': 0,
        'main_url': main_url,
        'competitor_urls': competitor_urls,
        'lighthouse_results': [],
        'screenshots': [],
        'aggregated_metrics': {},
        'recommendations': [],
        'errors': []
    }

    background_tasks.add_task(run_analysis, job_id, main_url, competitor_urls)

    return AnalysisStatus(
        job_id=job_id,
        status="queued",
        progress=0,
        current_step="Initializing analysis"
    )

@app.get("/api/status/{job_id}", response_model=AnalysisStatus)
async def get_status(job_id: str):
    """Get analysis status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    return AnalysisStatus(
        job_id=job_id,
        status=job.get('status', 'unknown'),
        progress=job.get('progress', 0),
        current_step=job.get('status', 'Processing'),
        results=job.get('aggregated_metrics') if job.get('status') == 'completed' else None,
        error='; '.join(job.get('errors', [])) if job.get('errors') else None
    )

@app.get("/api/results/{job_id}")
async def get_results(job_id: str):
    """Get complete analysis results"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job.get('status') != 'completed':
        raise HTTPException(status_code=400, detail="Analysis not completed")
    
    return {
        "job_id": job_id,
        "main_url": job['main_url'],
        "lighthouse_results": job.get('lighthouse_results', []),
        "screenshots": job.get('screenshots', []),
        "aggregated_metrics": job.get('aggregated_metrics', {}),
        "recommendations": job.get('recommendations', []),
        "errors": job.get('errors', [])
    }

@app.get("/api/download/{job_id}")
async def download_report(job_id: str):
    """Download PDF report"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job.get('status') != 'completed':
        raise HTTPException(status_code=400, detail="Report not ready")
    
    pdf_data = job.get('pdf_data', {})
    if not pdf_data.get('pdf_path'):
        raise HTTPException(status_code=404, detail="PDF not found")
    
    return FileResponse(
        pdf_data['pdf_path'],
        media_type='application/pdf',
        filename=f"performance_report_{job_id}.pdf"
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_jobs": len([j for j in jobs.values() if j.get('status') in ['queued', 'running']])
    }

@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job and cleanup resources"""
    if job_id in jobs:
        # Cleanup PDF file if exists
        pdf_path = jobs[job_id].get('pdf_data', {}).get('pdf_path')
        if pdf_path and os.path.exists(pdf_path):
            os.remove(pdf_path)
        
        del jobs[job_id]
        return {"message": "Job deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Job not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)