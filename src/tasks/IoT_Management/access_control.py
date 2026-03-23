"""Access control task for security & credentials monitoring."""
from crewai import Task

# 4.1 Security and Credentials Monitoring
from typing import Optional
def access_router(agent, device_id: Optional[str] = None, credentials: Optional[dict] = None):
    """Security and credentials monitoring task.
    
    Args:
        agent: The CrewAI agent to execute this task
        device_id: Target IoT device identifier
        credentials: Device credentials dictionary
    """
    return Task(
        description=f"Monitor security and validate credentials for IoT device {device_id}.",
        expected_output="Security compliance report with flow-based SDN data.",
        agent=agent
    )
