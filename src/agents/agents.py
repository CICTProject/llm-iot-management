"""
Agents module for managing different types of agents within the system.
- Define Crew Captain who orients other agents towards the autonomated orchestration goal of IOT device deployment in Software-Defined Networks (SDN) control.
    including security & credentials monitoring, deployment monitoring, plan validation, network auto-configuration, and device orchestration.

"""
import os
from textwrap import dedent
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI

from src.prompts import load_prompt
from src.mcp import (
    DeploymentMonitoringTool,
    DeviceOrchestrationTool,
    NetworkConfigurationTool,
    PlanValidationTool,
    EdgeAnomalyDetectionTool,
)

class CustomAgent:
    def __init__(self, name, role):
        # Use Google Gemini LLM via LangChain
        api_key = os.getenv("MODEL_API_KEY") 
        model = os.getenv("MODEL_NAME")
        
        if not api_key:
            raise ValueError("MODEL_API_KEY environment variable is not set. Please add your Google API key to the .env file.")
        
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0.7
        )
        self.name = name
        self.role = role

        # Create specialized MCP tools for each agent role
        self.deployment_tool = DeploymentMonitoringTool()
        self.orchestration_tool = DeviceOrchestrationTool()
        self.network_tool = NetworkConfigurationTool()
        self.validation_tool = PlanValidationTool()
        self.edge_tool = EdgeAnomalyDetectionTool()
        
    
    # 4.1 Define Cloud LLM Agent for sensor data collection in terms of patient fall detection
    def device_monitoring(self):
        return Agent(
            role="Device Monitoring Agent",
            backstory=dedent("""Monitors the camera-based IOT devices in the patient fall detection system."""),
            goal = dedent("""
            Monitor the camera-based IOT devices in the patient fall detection system, 
            including collecting sensor data related to camera feeds to detect potential fall events, analyzing the data to identify such events, and reporting any issues for further action."""),
            tools = [self.deployment_tool],
            verbose = True,
            llm=self.llm,
        )

    # 4.2 Define Edge LLM Agent for sensor data anomaly detection
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
    
    # 4.3 Define orchestration agent 
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
        
    # 4.4 Define plan validation agent 
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
    
    # 4.5 Define network auto-configuration agent 
    def network_auto_configuration(self):
        """Define agent for automatic network configuration."""
        prompt = load_prompt("system-management", "network_configuration")
        return Agent(
            role="Network Auto-Configuration Agent",
            backstory=prompt,
            goal=dedent("""
            Automatically configure Software-Defined Network flows for optimal IoT device communication,
            ensuring secure and efficient connectivity according to deployment topology."""),
            tools=[self.network_tool],
            verbose=True,
            llm=self.llm,
        )

    # 4.6 Define deployment monitoring agent (Data collection for diagnosis support)
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
    