"""Deployment monitoring task."""
from typing import Optional
from crewai import Task
from src.mcp import DeploymentMonitoringTool

# 1.3 Deployment Monitoring
def deployment_router(agent, device_ip: Optional[str] = None, location: Optional[str] = None):
    """Monitor IoT devices deployment status.
    
    Args:
        agent: The CrewAI agent to execute this task
        device_ip: Optional IP address to filter devices
        location: Optional location to filter devices
    """
    deployment_tool = DeploymentMonitoringTool()
    
    return Task(
        description=f"Monitor deployment status of IoT devices with IP {device_ip} and location {location}.",
        expected_output="Real-time deployment status report with device tracking and network topology.",
        tools=[deployment_tool],
        agent=agent
    )