"""
LangGraph workflow for website performance analysis with multiple agents
"""
from typing import TypedDict, List, Dict, Any, Annotated
import operator
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
import asyncio
from datetime import datetime

from app.agents.lighthouse_agent import LighthouseAgent
from app.agents.screenshot_agent import ScreenshotAgent
from app.agents.analysis_agent import AnalysisAgent
from app.agents.report_agent import ReportAgent
from app.config import settings

# WebPageTest and GTmetrix agents not used in Lighthouse-only mode
# from agents.webpagetest_agent import WebPageTestAgent
# from agents.gtmetrix_agent import GTMetrixAgent


class AnalysisState(TypedDict):
    """State schema for the analysis workflow"""
    job_id: str
    main_url: str
    competitor_urls: List[str]

    # Results from different agents
    lighthouse_results: Annotated[List[Dict[str, Any]], operator.add]
    webpagetest_results: Annotated[List[Dict[str, Any]], operator.add]
    gtmetrix_results: Annotated[List[Dict[str, Any]], operator.add]
    screenshots: Annotated[List[Dict[str, Any]], operator.add]

    # Aggregated analysis
    aggregated_metrics: Dict[str, Any]
    recommendations: List[str]

    # Report generation
    pdf_data: Dict[str, Any]

    # Status tracking
    status: str
    progress: int
    errors: Annotated[List[str], operator.add]


async def initialize_node(state: AnalysisState) -> AnalysisState:
    """Initialize the workflow"""
    print(f"[INIT] Initializing analysis for job {state['job_id']}")
    state['status'] = 'running'
    state['progress'] = 5
    return state


async def lighthouse_node(state: AnalysisState) -> AnalysisState:
    """Run Lighthouse analysis for all URLs"""
    print(f"[LIGHTHOUSE] Running Lighthouse analysis...")

    agent = LighthouseAgent()
    all_urls = [state['main_url']] + state['competitor_urls']

    results = []
    for url in all_urls:
        try:
            result = await agent.analyze(url)
            results.append({
                'url': url,
                'is_main': url == state['main_url'],
                'data': result,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            state['errors'].append(f"Lighthouse error for {url}: {str(e)}")

    state['lighthouse_results'] = results
    state['progress'] = 25
    return state


async def webpagetest_node(state: AnalysisState) -> AnalysisState:
    """Skip WebPageTest analysis (Lighthouse-only mode)"""
    print(f"[SKIP] Skipping WebPageTest analysis (not configured)")
    state['webpagetest_results'] = []
    state['progress'] = 45
    return state


async def gtmetrix_node(state: AnalysisState) -> AnalysisState:
    """Skip GTmetrix analysis (Lighthouse-only mode)"""
    print(f"[SKIP] Skipping GTmetrix analysis (not configured)")
    state['gtmetrix_results'] = []
    state['progress'] = 60
    return state


async def screenshot_node(state: AnalysisState) -> AnalysisState:
    """Capture screenshots for all URLs"""
    print(f"[SCREENSHOT] Capturing screenshots...")

    agent = ScreenshotAgent()
    all_urls = [state['main_url']] + state['competitor_urls']

    results = []
    for url in all_urls:
        try:
            result = await agent.capture(url, state['job_id'])
            results.append({
                'url': url,
                'is_main': url == state['main_url'],
                'data': result,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            state['errors'].append(f"Screenshot error for {url}: {str(e)}")

    state['screenshots'] = results
    state['progress'] = 70
    return state


async def analysis_node(state: AnalysisState) -> AnalysisState:
    """Aggregate and analyze all metrics using AI"""
    print(f"[AI] Analyzing metrics and generating recommendations...")

    agent = AnalysisAgent()

    try:
        # Aggregate all metrics
        aggregated = await agent.aggregate_metrics(
            lighthouse=state['lighthouse_results'],
            webpagetest=state['webpagetest_results'],
            gtmetrix=state['gtmetrix_results']
        )

        # Generate AI-powered recommendations
        recommendations = await agent.generate_recommendations(
            main_url=state['main_url'],
            aggregated_metrics=aggregated
        )

        state['aggregated_metrics'] = aggregated
        state['recommendations'] = recommendations
        state['progress'] = 85

    except Exception as e:
        state['errors'].append(f"Analysis error: {str(e)}")

    return state


async def report_node(state: AnalysisState) -> AnalysisState:
    """Generate PDF report with all findings"""
    print(f"[PDF] Generating PDF report...")

    agent = ReportAgent()

    try:
        pdf_data = await agent.generate_report(
            job_id=state['job_id'],
            main_url=state['main_url'],
            competitor_urls=state['competitor_urls'],
            lighthouse_results=state['lighthouse_results'],
            webpagetest_results=state['webpagetest_results'],
            gtmetrix_results=state['gtmetrix_results'],
            screenshots=state['screenshots'],
            aggregated_metrics=state['aggregated_metrics'],
            recommendations=state['recommendations']
        )

        state['pdf_data'] = pdf_data
        state['progress'] = 100
        state['status'] = 'completed'

    except Exception as e:
        state['errors'].append(f"Report generation error: {str(e)}")
        state['status'] = 'failed'

    return state


def create_analysis_graph() -> StateGraph:
    """Create the LangGraph workflow for performance analysis"""

    # Create the graph
    workflow = StateGraph(AnalysisState)

    # Add nodes (Lighthouse-only mode - skip webpagetest and gtmetrix)
    workflow.add_node("initialize", initialize_node)
    workflow.add_node("lighthouse", lighthouse_node)
    # workflow.add_node("webpagetest", webpagetest_node)  # Not used in Lighthouse-only mode
    # workflow.add_node("gtmetrix", gtmetrix_node)  # Not used in Lighthouse-only mode
    workflow.add_node("capture_screenshots", screenshot_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("report", report_node)

    # Define the flow
    workflow.set_entry_point("initialize")

    # Simplified flow - Lighthouse only for now
    # Skip WebPageTest and GTmetrix nodes for faster analysis
    workflow.add_edge("initialize", "lighthouse")
    workflow.add_edge("lighthouse", "capture_screenshots")
    workflow.add_edge("capture_screenshots", "analysis")
    workflow.add_edge("analysis", "report")
    workflow.add_edge("report", END)

    # Compile the graph
    return workflow.compile()


# For parallel execution (alternative approach)
def create_parallel_analysis_graph() -> StateGraph:
    """Create the LangGraph workflow with parallel execution of performance tests"""

    workflow = StateGraph(AnalysisState)

    # Add nodes
    workflow.add_node("initialize", initialize_node)
    workflow.add_node("lighthouse", lighthouse_node)
    workflow.add_node("webpagetest", webpagetest_node)
    workflow.add_node("gtmetrix", gtmetrix_node)
    workflow.add_node("screenshots", screenshot_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("report", report_node)

    # Define parallel flow
    workflow.set_entry_point("initialize")

    # Run performance tests in parallel
    workflow.add_edge("initialize", "lighthouse")
    workflow.add_edge("initialize", "webpagetest")
    workflow.add_edge("initialize", "gtmetrix")

    # Wait for all tests before screenshots
    workflow.add_edge("lighthouse", "screenshots")
    workflow.add_edge("webpagetest", "screenshots")
    workflow.add_edge("gtmetrix", "screenshots")

    # Continue with analysis and report
    workflow.add_edge("screenshots", "analysis")
    workflow.add_edge("analysis", "report")
    workflow.add_edge("report", END)

    return workflow.compile()
