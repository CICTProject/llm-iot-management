"""Deployment monitoring task."""
from typing import Optional
from crewai import Task

# 4.2 Deployment Monitoring
def deployment_router(agent, device_ip: Optional[str] = None, location: Optional[str] = None):
    """Monitor IoT device deployment status.
    
    Args:
        agent: The CrewAI agent to execute this task
        device_ip: IP address of the device to monitor
        location: Physical location of the device
    """
    return Task(
        description=f"Monitor deployment status of IoT device at {device_ip} in {location}.",
        expected_output="Deployment status report with device IPs, locations, and services.",
        agent=agent
    )
