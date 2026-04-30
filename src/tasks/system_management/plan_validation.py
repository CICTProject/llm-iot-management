"""Plan validation task."""
from typing import Optional
from crewai import Task
from src.mcp import PlanValidationTool

# 4.4 Plan Validation
def validation_router(agent, plan_id: Optional[str] = None, requirements: Optional[dict] = None):
    """Validate IoT deployment plan.
    
    Args:
        agent: The CrewAI agent to execute this task
        plan_id: Deployment plan identifier
        requirements: System requirements dictionary
    """
    validation_tool = PlanValidationTool()

    return Task(
        description=f"Validate deployment plan {plan_id} meets system requirements.",
        expected_output="Validation report with recommendations.",
        tools=[validation_tool],
        agent=agent
    )

