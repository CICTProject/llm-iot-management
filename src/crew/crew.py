"""Custom Crew AI module for LLM Multi Agent Management."""
from dotenv import load_dotenv
from crewai import Crew

from src.agents.agents import CustomAgent
from src.tasks.system_management import (
    device_monitoring_router,
    device_router,
    deployment_router,
    network_config_router,
    validation_router,
)
from src.tasks.edge_detection import edge_router

load_dotenv()


class CustomCrew:
    def __init__(self):
        self.agents = CustomAgent("crew", "orchestrator")
        
    def run_all(self):
        """Run all 6 agents and tasks."""
        device_monitoring_agent = self.agents.device_monitoring()
        edge_anomaly_agent = self.agents.edge_anomaly_detection()
        orchestration_agent = self.agents.orchestration()
        validation_agent = self.agents.plan_validation()
        network_agent = self.agents.network_auto_configuration()
        deployment_agent = self.agents.deployment_monitoring()
        
        # Create tasks for all agents using routers
        device_monitoring_task = device_monitoring_router(device_monitoring_agent)
        edge_task = edge_router(edge_anomaly_agent)
        orchestration_task = device_router(orchestration_agent)
        validation_task = validation_router(validation_agent)
        network_task = network_config_router(network_agent)
        deployment_task = deployment_router(deployment_agent)
        
        crew = Crew(
            agents=[device_monitoring_agent, edge_anomaly_agent, orchestration_agent,
                    validation_agent, network_agent, deployment_agent],
            tasks=[device_monitoring_task, edge_task, orchestration_task,
                   validation_task, network_task, deployment_task],
            verbose=True,
        )
        return crew.kickoff()
    
    def run_device_monitoring(self):
        """Run device monitoring agent only."""
        agent = self.agents.device_monitoring()
        task = device_monitoring_router(agent)
        return Crew(agents=[agent], tasks=[task], verbose=True).kickoff()
    
    def run_edge_anomaly_detection(self):
        """Run edge anomaly detection agent only."""
        agent = self.agents.edge_anomaly_detection()
        task = edge_router(agent)
        return Crew(agents=[agent], tasks=[task], verbose=True).kickoff()
    
    def run_orchestration(self):
        """Run device orchestration agent only."""
        agent = self.agents.orchestration()
        task = device_router(agent)
        return Crew(agents=[agent], tasks=[task], verbose=True).kickoff()
    
    def run_plan_validation(self):
        """Run plan validation agent only."""
        agent = self.agents.plan_validation()
        task = validation_router(agent)
        return Crew(agents=[agent], tasks=[task], verbose=True).kickoff()
    
    def run_network_auto_configuration(self):
        """Run network auto-configuration agent only."""
        agent = self.agents.network_auto_configuration()
        task = network_config_router(agent)
        return Crew(agents=[agent], tasks=[task], verbose=True).kickoff()
    
    def run_deployment_monitoring(self):
        """Run deployment monitoring agent only."""
        agent = self.agents.deployment_monitoring()
        task = deployment_router(agent)
        return Crew(agents=[agent], tasks=[task], verbose=True).kickoff()
