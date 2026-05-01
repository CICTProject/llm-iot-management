"""
Medical Sensor Deployment MCP Server.
FastMCP server with unified CrewAI tool wrappers for each agent role.
"""
from mcp.server.fastmcp import FastMCP

# Create shared FastMCP server instance
mcp_server = FastMCP("Deployment Monitoring MCP")

# Export unified tools for different agent roles
from .main import (
    DeploymentMonitoringTool,
    DeviceOrchestrationTool,
    PlanValidationTool,
    PlanExecutionTool,
    EdgeAnomalyDetectionTool,
    get_mcp_tool,
)

__all__ = [
    "mcp_server",
    "DeploymentMonitoringTool",
    "DeviceOrchestrationTool",
    "PlanValidationTool",
    "EdgeAnomalyDetectionTool",
    "PlanExecutionTool",
    "get_mcp_tool",
]
