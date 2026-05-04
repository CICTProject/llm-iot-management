# LLM-Based Intent Orchestration for Medical Internet of Things (IoT) Environments

## Overview

Modern medical research laboratories increasingly integrate smart workspace environments with diverse IoT devices and services. However, clinicians, nurses, and researchers—typically non-IT specialists—require intuitive mechanisms to express their operational intents without manual device configuration. LLMs offer promising capabilities in reasoning, planning, and task orchestration, enabling seamless automation of data retrieval, analysis, and workflow execution. Nevertheless, relying only on cloud-based intelligence may introduce latency and limit immediate responsiveness in emergency situations, especially when rapid decisions are required for IoT device monitoring and alerting. To address this limitation, our proposed IEEE 802.15.11 intent-based wireless BioAI-powered edge-cloud healthcare IoT system integrates an Edge Anomaly Detection model, implemented as a lightweight distilled student AI model deployed at the edge layer. This model continuously monitors sensor data and device health metrics by comparing real-time values with historical patterns and predefined device-status thresholds. When deviations exceed normal operating ranges, the edge model immediately detects anomalies and generates alerts locally, enabling fast emergency response without waiting for cloud-side reasoning.

At the cloud layer, the system relies on multiple AI agents and LLM-based orchestration to support higher-level reasoning, planning, and deployment decisions. The LLM-driven deployment engine enables clinicians to interact with medical datasets, IoT-connected sequencing devices, AI models, and physical IoT devices through natural language queries. The system further supports intelligent recommendations for activating, configuring, and allocating multiple IoT devices by considering energy resources, device status, patient behavior, and monitoring priorities. This allows the platform to maximize patient monitoring coverage while maintaining energy efficiency. 

At the edge layer, the proposed architecture (Figure 1) combines low-latency edge intelligence for anomaly detection with cloud-based multi-agent LLM orchestration for adaptive deployment, recommendation, and workflow automation in medical research laboratory environments.This project aims to the second-round candidation of Concours Innovation Creative Challenge 2026 in the intersection domain between IOT, Intelligence Artificielle (AI) and Edge-Cloud Computing. Our complete work presents in [CICT Hackathon Round 2 Presentation](https://docs.google.com/presentation/d/1wKNIP_Rr-3uXvEWs3CL8ITc8lvj-x6bo/edit?slide=id.g3d121bd3dce_1_14#slide=id.g3d121bd3dce_1_14).

![Data Auto-Collection in IOT Smart Healthcare Systems](docs/general-architecture/architecture.png)
*Figure 1: Conceptual Architecture in IOT Smart Healthcare Systems*
## Application Scenarios

| Demo | Version | Workflow Video   | Description |
|---------|---------|---------------|----------------|
| Round 1 | v1.0.1  | [![Thumbnail](https://img.youtube.com/vi/ad-wvToCBss/maxresdefault.jpg)](https://youtu.be/ad-wvToCBss) | Initial project demo in two main scenarios. |

### Scenario 1: Edge-based Real-Time Physiological Monitoring
Wearable and implantable sensors continuously monitor vital signs (blood pressure, heart rate) with anomaly detection and able to run in ressource-constrainted IOT edge devices.

[![Edge AI Anomalies Detection Demo](https://img.youtube.com/vi/SEqdKKrjr5g/maxresdefault.jpg)](https://youtu.be/SEqdKKrjr5g)
*Prototype Alpha v1.0.1: Workflow Demo in Edge Anomaly Detection scenario*

**Research Direction:** Edge-based lightweight patient prediction models (distillation) running directly on sensor devices.

### Scenario 2: Cloud-based Smart Hospital BioIOT Management 
Camera-based monitoring systems detect resident falls, autonomous medical IOT sensors/actuators management, enhancing safety, performance, energy-awareness while reducing staff workload in cloud-based ressources.

[![LLM Intent Orchestration Demo](https://img.youtube.com/vi/Og8NFQ0c9E4/maxresdefault.jpg)](https://youtu.be/Og8NFQ0c9E4)
*Prototype Alpha v1.0.1: Workflow Demo in IOT device orchestration scenario*

**Research Direction:** Generative AI multi-agent for task orchestration, deployment, auto-configuration, plan validation and execution.

---

## Project Structure

```
llm-intent-orchestration/
├── src/
│   ├── main.py              # CLI entry point in FastMCP server with menu interface
│   ├── crew.py              # Multi-agent orchestration
│   ├── agents/
│   │   └── agents.py        # LLM Agent logic
│   ├── tasks/               # Task router 
│   ├── mcp/                 # MCP Server tools
│   ├── prompts/             # System prompts
│   ├── utils/               # External task tools
│   └── db/                  # Database
├── configs/                 # Configuration files
├── tests/                   # Unit tests
├── docs/                    # Documentation
├── tools/                   # Tools
├── data/                    # Data
└── .env                     # Environment variables
```

---

## Quick Setup

### Prerequisites
- Install pipx: [github.com/pypa/pipx](https://github.com/pypa/pipx)
- Install Poetry: [python-poetry.org/docs](https://python-poetry.org/docs)

### Installation
```bash
# Verify Poetry installation
poetry --version

# Install dependencies
python -m poetry install (--verbose)

# Check virtual environment
poetry env list
source $(poetry env info --path)/bin/activate

# Or for Poetry 1.x
poetry shell

```

### Running the Application

Our project runs InfluxDB locally on Windowns before running the database seeding step by executing `influxd` from `C:\Users\Admin\InfluxData`; the service runs at `http://localhost:8086` and should be configured with the `medical` organization, `medical_sensors` bucket, and a valid API token as described in [InfluxDB v2 documentation](https://docs.influxdata.com/influxdb/v2).

```bash
# Seed database mitigation (Future replacement with real-time iot device data)
python -m poetry run python -m src.db.main 
# Uvicorn App
python -m poetry run uvicorn src.main:app --host 0.0.0.0 --port 8001
```
> [!TIP]
> All API documents & functionality tests in http://localhost:8001/docs, with current APIs endpoints including crew execution (**POST** `/v1/crew/execute`, **GET** `/v1/crew/execution/{execution_id}`, **GET** `/v1/crew/executions`), chat completions supports 3 LLM models (**GET** `/v1/models`, **POST** `/v1/chat/completions`) and system status (**GET** `/v1/health`, **GET** `/v1/status`).

---

## References

1. MCP SDK Integration: [modelcontextprotocol.io/docs/sdk](https://modelcontextprotocol.io/docs/sdk)
2. CrewAI Task Automation: [docs.crewai.com/en/mcp/overview](https://docs.crewai.com/en/mcp/overview)
3. CrewAI Tutorial: [youtu.be/sPzc6hMg7So](https://www.youtube.com/watch?v=sPzc6hMg7So)
4. MCP Learning Resources: [youtu.be/QIOk4XZ5XNU](https://youtu.be/QIOk4XZ5XNU)
5. CrewAI + FastMCP: [github.com/ashishpatel26/Crewai-MCP-Course](https://github.com/ashishpatel26/Crewai-MCP-Course)
6. Integration with FastMCP via [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
7. ONOS MCP Server (Code inspiration):[onos-mcp-server](https://github.com/MCP-Mirror/davidlin2k_onos-mcp-server)
