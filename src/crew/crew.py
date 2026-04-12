"""Custom Crew AI module for LLM Multi Agent Management."""
from dotenv import load_dotenv
from crewai import Crew

from src.agents.agents import CustomAgent
from src.tasks.system_management import (
    device_router,
    deployment_router,
    validation_router,
)
from src.tasks.edge_detection import edge_router

load_dotenv()


class CustomCrew:
    def __init__(self):
        self.agents = CustomAgent("crew", "orchestrator")
        
    def run_all(self):
        """Run all agents and tasks."""
        edge_anomaly_agent = self.agents.edge_anomaly_detection()
        orchestration_agent = self.agents.orchestration()
        validation_agent = self.agents.plan_validation()
        deployment_agent = self.agents.deployment_monitoring()
        
        # Create tasks for all agents using routers
        edge_task = edge_router(edge_anomaly_agent)
        orchestration_task = device_router(orchestration_agent)
        validation_task = validation_router(validation_agent)
        deployment_task = deployment_router(deployment_agent)
        
        crew = Crew(
            agents=[edge_anomaly_agent, orchestration_agent,
                    validation_agent, deployment_agent],
            tasks=[edge_task, orchestration_task,
                   validation_task, deployment_task],
            verbose=True,
        )
        return crew.kickoff()
    
    # 1.1 Run edge anomaly detection agent
    def run_edge_anomaly_detection(self):
        """Run edge anomaly detection agent only."""
        agent = self.agents.edge_anomaly_detection()
        task = edge_router(agent)
        return Crew(agents=[agent], tasks=[task], verbose=True).kickoff()
    
    # 1.3 Run device orchestration agent
    def run_orchestration(self):
        """Run device orchestration agent only."""
        agent = self.agents.orchestration()
        task = device_router(agent)
        return Crew(agents=[agent], tasks=[task], verbose=True).kickoff()
    
    # 1.4 Run plan validation agent
    def run_plan_validation(self):
        """Run plan validation agent only."""
        agent = self.agents.plan_validation()
        task = validation_router(agent)
        return Crew(agents=[agent], tasks=[task], verbose=True).kickoff()
    
