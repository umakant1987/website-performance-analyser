# MCP Servers for Website Performance Analyzer

This directory contains Model Context Protocol (MCP) servers that can be used to extend the functionality of the performance analyzer.

## What is MCP?

Model Context Protocol (MCP) is a standardized protocol that allows AI agents to interact with external tools and services in a consistent way. Each MCP server exposes a set of tools that agents can discover and use.

## Architecture Benefits

Using MCP servers provides several advantages:

1. **Modularity**: Each performance testing service is an independent, reusable component
2. **Scalability**: MCP servers can run on different machines for distributed testing
3. **Reusability**: Same MCP servers can be used across different projects
4. **Error Isolation**: Issues in one service don't affect others
5. **Tool Discovery**: Agents automatically discover available tools

## Recommended MCP Servers

### 1. Lighthouse MCP Server
- **Purpose**: Run Lighthouse performance audits
- **Tools**:
  - `run_lighthouse_audit`: Run a full Lighthouse audit
  - `get_web_vitals`: Extract Web Vitals metrics
  - `analyze_performance`: Get performance recommendations

### 2. WebPageTest MCP Server
- **Purpose**: Interface with WebPageTest API
- **Tools**:
  - `submit_test`: Submit a URL for testing
  - `get_test_results`: Retrieve test results
  - `get_waterfall`: Get waterfall chart data

### 3. GTmetrix MCP Server
- **Purpose**: Interface with GTmetrix API
- **Tools**:
  - `run_test`: Run GTmetrix test
  - `get_report`: Retrieve detailed report
  - `compare_results`: Compare multiple test results

### 4. Screenshot MCP Server
- **Purpose**: Capture website screenshots
- **Tools**:
  - `capture_screenshot`: Take screenshot with specific viewport
  - `capture_multiple_devices`: Capture across devices
  - `capture_fullpage`: Take full-page screenshot

### 5. Report Generator MCP Server
- **Purpose**: Generate PDF/HTML reports
- **Tools**:
  - `generate_pdf_report`: Create PDF report
  - `generate_html_report`: Create HTML report
  - `customize_template`: Use custom report template

## Implementation Options

### Option 1: Standalone MCP Servers (Recommended)

Each service runs as a separate MCP server that the LangGraph agents can connect to.

**Pros**:
- True microservices architecture
- Independent scaling and deployment
- Language-agnostic (servers can be in Python, Node.js, etc.)
- Better error isolation

**Cons**:
- More complex deployment
- Network latency between services
- Requires MCP server infrastructure

### Option 2: Embedded Agents (Current Implementation)

Agents are directly embedded in the Python application as classes.

**Pros**:
- Simpler deployment (single application)
- No network overhead
- Easier for development and testing

**Cons**:
- Tightly coupled components
- Harder to scale independently
- Less reusable across projects

## Creating a Custom MCP Server

Here's a template for creating an MCP server:

```python
from mcp import Server, Tool
from typing import Dict, Any

class PerformanceTestMCPServer(Server):
    """MCP Server for performance testing"""

    def __init__(self):
        super().__init__(name="performance-test-server")
        self.register_tools()

    def register_tools(self):
        """Register available tools"""

        @self.tool(
            name="run_lighthouse_audit",
            description="Run a Lighthouse performance audit on a URL",
            parameters={
                "url": {"type": "string", "description": "URL to audit"},
                "device": {"type": "string", "enum": ["desktop", "mobile"]}
            }
        )
        async def run_lighthouse_audit(url: str, device: str = "desktop") -> Dict[str, Any]:
            # Implementation
            pass

if __name__ == "__main__":
    server = PerformanceTestMCPServer()
    server.run()
```

## Integration with LangGraph

To use MCP servers with LangGraph:

```python
from langgraph.prebuilt import ToolNode
from mcp import MCPClient

# Connect to MCP servers
lighthouse_client = MCPClient("http://localhost:8001")
webpagetest_client = MCPClient("http://localhost:8002")

# Discover tools
lighthouse_tools = await lighthouse_client.list_tools()
webpagetest_tools = await webpagetest_client.list_tools()

# Create tool nodes
lighthouse_node = ToolNode(lighthouse_tools)
webpagetest_node = ToolNode(webpagetest_tools)

# Add to workflow
workflow.add_node("lighthouse", lighthouse_node)
workflow.add_node("webpagetest", webpagetest_node)
```

## Configuration

Add MCP server endpoints to your `.env` file:

```env
MCP_LIGHTHOUSE_URL=http://localhost:8001
MCP_WEBPAGETEST_URL=http://localhost:8002
MCP_GTMETRIX_URL=http://localhost:8003
MCP_SCREENSHOT_URL=http://localhost:8004
MCP_REPORT_URL=http://localhost:8005
```

## Future Enhancements

1. **Authentication**: Add API key authentication for MCP servers
2. **Rate Limiting**: Implement rate limiting per client
3. **Caching**: Add caching layer for repeated requests
4. **Monitoring**: Add health checks and monitoring
5. **Load Balancing**: Distribute requests across multiple instances

## When to Use MCP vs Direct Integration

**Use MCP servers when**:
- Building a production system that needs to scale
- Multiple projects need the same functionality
- Services need to run on different infrastructure
- You want language-agnostic components

**Use direct integration (current approach) when**:
- Building a prototype or MVP
- Simplicity and deployment ease are priorities
- All services can run in a single Python application
- Network latency is a concern
