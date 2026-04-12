"""Device monitoring task for camera-based IoT devices."""
from typing import Optional
from crewai import Task

# 4.1 Device Monitoring
def device_monitoring_router(agent, device_id: Optional[str] = None, location: Optional[str] = None):
    """Monitor camera-based IoT devices and collect sensor data.
    
    Args:
        agent: The CrewAI agent to execute this task
        device_id: Optional device identifier to focus monitoring
        location: Optional location to filter devices
    """
    return Task(
        description=f"Monitor camera-based IoT devices for fall detection and sensor data collection at location {location}.",
        expected_output="Device monitoring report with sensor data, status, and alerts.",
        agent=agent
    )
