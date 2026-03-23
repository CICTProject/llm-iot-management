"""
Agents module for managing different types of agents within the system.
- Define Crew Captain who orients other agents towards the autonomated orchestration goal of IOT device deployment in Software-Defined Networks (SDN) control.
    including security & credentials monitoring, deployment monitoring, plan validation, network auto-configuration, and device orchestration.

"""
import os
from textwrap import dedent
from crewai import Agent, LLM
from crewai_tools import (
    JSONSearchTool,
    WebsiteSearchTool
)

class CustomAgent:
    def __init__(self, name, role):
        # Use Google Gemini
        self.llm = LLM(
            model="gemini/gemini-flash-latest",
            api_key=os.getenv("GEMINI_API_KEY")
        )
        self.name = name
        self.role = role
        
    # 4.1 Define Cloud LLM Agent for sensor data collection in terms of patient fall detection
    def device_monitoring(self):
        return Agent(
            role="Device Monitoring Agent",
            backstory=dedent("""Monitors the camera-based IOT devices in the patient fall detection system."""),
            goal = dedent("""
            Monitor the camera-based IOT devices in the patient fall detection system, 
            including collecting sensor data related to camera feeds to detect potential fall events, analyzing the data to identify such events, and reporting any issues for further action."""),
            tools = [JSONSearchTool()],
            verbose = True,
            llm=self.llm,
        )

    # 4.2 Define Edge LLM Agent for sensor data anomaly detection (Future work - Giang)
    
    # 4.3 Define Diagnosis LLM Agent for doctor's diagnosis support  (Data tools using website search and JSON search for patient history, data from IOT devices in the deployment monitoring) 
    def diagnosis_support(self):
        return Agent(
            role="Diagnosis Support Agent",
            backstory=dedent("""Supports doctors in diagnosing patient conditions based on data from IOT devices and patient history."""),
            goal = dedent("""
            Provide support to doctors in diagnosing patient conditions by analyzing data from IOT devices in the fall detection scenario to know about patient conditions and patient history,
            include generating recommendations for diagnosis and relevant medical actions step by step with explanations, and report any issues for further action."""),
            tools = [JSONSearchTool(), WebsiteSearchTool()],
            verbose = True,
            llm=self.llm,
        )
                
    # 4.4 Define security & credentials monitoring agent (Future development)
    def security_credentials_monitoring(self):
        return Agent(
            role="Security & Credentials Monitoring Agent",
            backstory=dedent("""Monitors security and credentials for IOT devices, ensuring compliance with predefined rules and restrictions."""),
            goal = dedent("""
            Ensure compliance with predefined rules and restrictions for IOT devices environment,
            which satify deployment device status and reporting any security issues for further action.
            """),
            tools = [JSONSearchTool()],
            verbose = True,
            llm=self.llm,
        )
        
    # 4.5 Define orchestration agent (Future development)
    def orchestration(self):
        return Agent(
            role="Orchestration Agent",
            backstory=dedent("""Orchestrates the deployment of IOT devices in the patient fall detection system."""),
            goal = dedent("""
            Ensure that IOT devices are orchestrated according to the predefined rules and restrictions,
            include generating necessary IOT devices with their services in the deployment monitoring server, and the algorithm for network auto-configuration, and report any issues for further action."""),
            tools = [JSONSearchTool()],
            verbose = True,
            llm=self.llm,
        )
        
    # 4.6 Define plan validation agent (Future development)
    def plan_validation(self):
        return Agent(
            role="Plan Validation Agent",
            backstory=dedent("""Validates the deployment plan for IOT devices in the patient fall detection system."""),
            goal = dedent("""
            Ensure that the deployment plan for IOT devices is valid and meets the requirements of the patient fall detection system,
            include generating recommendations for improving the deployment plan based on the security and credentials monitoring to reach the device rules and policies, deployment monitoring, and orchestration agents, and report any issues for further action."""),
            tools = [JSONSearchTool()],
            verbose = True,
            llm=self.llm,
        )
    
    # 4.7 Define network auto-configuration agent (Future development)
    def network_auto_configuration(self):
        return Agent(
            role="Network Auto-Configuration Agent",
            backstory=dedent("""Automatically configures the network for IOT devices in the patient fall detection system."""),
            goal = dedent("""
            Ensure that the network for IOT devices is automatically configured according to the predefined rules and restrictions 
            for network auto-configuration based on the deployment status of each device, and report any issues for further action."""),
            tools = [JSONSearchTool()],
            verbose = True,
            llm=self.llm,
        )

    # 4.8 Define deployment monitoring agent (Data collection for diagnosis support)
    def deployment_monitoring(self):
        return Agent(
            role="Deployment Monitoring Agent",
            backstory=dedent("""Monitors the deployment of IOT devices in the patient fall detection system."""),
            goal = dedent("""
            Ensure that IOT devices are deployed according to the safety of patient moving patterns and the predefined rules and restrictions,
            include deployment status of each device (ip address, status, location and relevant services), and report any issues for further action.
            """),
            tools = [JSONSearchTool()],
            verbose = True,
            llm=self.llm,
        )  