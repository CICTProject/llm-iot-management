"""Custom Crew AI module for LLM Multi Agent Management."""
from dotenv import load_dotenv
from crewai import Crew

from agents.agents import CustomAgent
from tasks.IoT_Management import (
    access_router,
    device_router,
    deployment_router,
    network_config_router,
    validation_router,
    diagnosis_router,
)
from tasks.Edge_Detection import edge_router

load_dotenv()


class CustomCrew:
    def __init__(self):
        self.agents = CustomAgent("crew", "orchestrator")
        
    def run_all(self):
        """Run all agents and tasks."""
        security_agent = self.agents.security_credentials_monitoring()
        deployment_agent = self.agents.deployment_monitoring()
        orchestration_agent = self.agents.orchestration()
        validation_agent = self.agents.plan_validation()
        network_agent = self.agents.network_auto_configuration()
        diagnosis_agent = self.agents.diagnosis_support()
        
        security_task = access_router(security_agent)
        deployment_task = deployment_router(deployment_agent)
        orchestration_task = device_router(orchestration_agent)
        validation_task = validation_router(validation_agent)
        network_task = network_config_router(network_agent)
        diagnosis_task = diagnosis_router(diagnosis_agent)
        
        crew = Crew(
            agents=[security_agent, deployment_agent, orchestration_agent,
                    validation_agent, network_agent, diagnosis_agent],
            tasks=[security_task, deployment_task, orchestration_task,
                   validation_task, network_task, diagnosis_task],
            verbose=True,
        )
        return crew.kickoff()
    
    def run_security(self):
        """Run security monitoring only."""
        agent = self.agents.security_credentials_monitoring()
        task = access_router(agent)
        return Crew(agents=[agent], tasks=[task], verbose=True).kickoff()
    
    def run_deployment(self):
        """Run deployment monitoring only."""
        agent = self.agents.deployment_monitoring()
        task = deployment_router(agent)
        return Crew(agents=[agent], tasks=[task], verbose=True).kickoff()
    
    def run_orchestration(self):
        """Run device orchestration only."""
        agent = self.agents.orchestration()
        task = device_router(agent)
        return Crew(agents=[agent], tasks=[task], verbose=True).kickoff()
    
    def run_network(self):
        """Run network configuration only."""
        agent = self.agents.network_auto_configuration()
        task = network_config_router(agent)
        return Crew(agents=[agent], tasks=[task], verbose=True).kickoff()
    
    def run_diagnosis(self):
        """Run diagnosis support only."""
        agent = self.agents.diagnosis_support()
        task = diagnosis_router(agent)
        return Crew(agents=[agent], tasks=[task], verbose=True).kickoff()
