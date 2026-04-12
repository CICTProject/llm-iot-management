"""Device orchestration task."""
from crewai import Task
from typing import Optional

# 4.3 Device Orchestration
def device_router(agent, device_list: Optional[list] = None, rules: Optional[dict] = None):
    """Orchestrate IoT device deployment.
    
    Args:
        agent: The CrewAI agent to execute this task
        device_list: List of IoT devices to orchestrate
        rules: Predefined deployment rules
    """
    return Task(
        description=f"Orchestrate {len(device_list) if device_list else 0} IoT devices according to predefined rules.",
        expected_output="Device orchestration plan with services and configurations.",
        agent=agent
    )
