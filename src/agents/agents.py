"""
Agents module for managing different types of agents within the system.
- Define Crew Captain who orients other agents towards the autonomated orchestration goal of IOT device deployment in Software-Defined Networks (SDN) control.
    including deployment monitoring, plan validation, and device orchestration.

"""
import os
from textwrap import dedent
from crewai import Agent, LLM

from src.prompts import load_prompt
from src.mcp import (
    DeploymentMonitoringTool,
    DeviceOrchestrationTool,
    PlanValidationTool,
    EdgeAnomalyDetectionTool,
    PlanExecutionTool,
)

class CustomAgent:
    def __init__(self, name, role):
        api_key = os.getenv("MODEL_API_KEY") 
        model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash")
        
        if model_name.startswith("gemini/"):
            if not api_key:
                raise ValueError("MODEL_API_KEY environment variable is not set. Please add your API key to the .env file.")
            # Clean up model name prefix
            if model_name.startswith("models/"):
                model_name = model_name.replace("models/", "")
            # LiteLLM backend 
            self.llm = LLM(
                model=model_name,
                api_key=api_key,
                temperature=0.7
            )
        if model_name.startswith("ollama/"):
            # Ollama backend
            self.llm = LLM(
                model=model_name,
                base_url="http://localhost:11434",
                temperature=0.7
            )
        self.name = name
        self.role = role

        # Create specialized MCP tools for each agent role
        self.deployment_tool = DeploymentMonitoringTool()
        self.orchestration_tool = DeviceOrchestrationTool()
        self.validation_tool = PlanValidationTool()
        self.edge_tool = EdgeAnomalyDetectionTool()
        self.execution_tool = PlanExecutionTool()
    
    # 1.1 Define Edge LLM Agent for sensor data anomaly detection
    def edge_anomaly_detection(self):
        """Define agent for anomaly detection in sensor data."""
        prompt = load_prompt("edge-detection", "edge_detection")
        return Agent(
            role="Anomaly Detection Agent",
            backstory=prompt,
            goal=dedent("""
            Detect anomalies in sensor data from camera-based IoT devices,
            including identifying potential fall events and sensor malfunctions for immediate alerting."""),
            tools=[self.edge_tool],
            verbose=True,
            llm=self.llm,
        )
    
    # 1.2 Define orchestration agent 
    def orchestration(self):
        """Define agent for IoT device orchestration."""
        prompt = load_prompt("system-management", "device_orchestration")
        return Agent(
            role="Orchestration Agent",
            backstory=prompt,
            goal=dedent("""
            Orchestrate IoT device deployment according to predefined rules and restrictions,
            ensuring optimal service configuration and healthcare safety requirements."""),
            tools=[self.orchestration_tool],
            verbose=True,
            llm=self.llm,
        )
        
    # 1.3 Define plan validation agent 
    def plan_validation(self):
        """Define agent for validating deployment plans."""
        prompt = load_prompt("system-management", "plan_validation")
        return Agent(
            role="Plan Validation Agent",
            backstory=prompt,
            goal=dedent("""
            Validate IoT deployment plans against system requirements and security policies,
            providing comprehensive validation reports and actionable recommendations."""),
            tools=[self.validation_tool],
            verbose=True,
            llm=self.llm,
        )

    # 1.4 Define deployment monitoring agent 
    def deployment_monitoring(self):
        """Define agent for monitoring IoT deployment status."""
        prompt = load_prompt("system-management", "deployment_monitoring")
        return Agent(
            role="Deployment Monitoring Agent",
            backstory=prompt,
            goal=dedent("""
            Monitor real-time deployment status of all IoT devices,
            ensuring patient safety through accurate device tracking and network topology awareness."""),
            tools=[self.deployment_tool],
            verbose=True,
            llm=self.llm,
        )
    
    # 1.5 Define plan execution agent
    def plan_execution(self):
        """Define agent for executing deployment plans."""
        prompt = load_prompt("system-management", "plan_execution")
        return Agent(
            role="Plan Execution Agent",
            backstory=prompt,
            goal=dedent("""
            Execute IoT deployment plans with various activation algorithms to actual device 
            states through communication protocols."""),
            tools=[self.execution_tool],
            verbose=True,
            llm=self.llm,
        )