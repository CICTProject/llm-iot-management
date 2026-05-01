"""Plan execution task."""
from typing import Optional
from crewai import Task
from src.mcp import PlanExecutionTool

# 1.5 Plan Execution
def execution_router(agent, plan_id: Optional[str] = None, requirements: Optional[dict] = None):
    """Execute IoT orchestration plan.
    
    Args:
        agent: The CrewAI agent to execute this task
        plan_id: Orchestration plan identifier
        requirements: System requirements dictionary
    """
    execution_tool = PlanExecutionTool()

    return Task(
        description=f"Execute orchestration plan {plan_id}.",
        expected_output="Execution report with status updates.",
        tools=[execution_tool],
        agent=agent
    )

