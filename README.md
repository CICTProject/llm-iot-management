# LLM-Based Intent Orchestration for Medical Internet of Things (IoT) Environments

## Overview

Modern medical research laboratories increasingly integrate smart workspace environments with diverse IoT devices and services. However, clinicians, nurses, and researchers—typically non-IT specialists—require intuitive mechanisms to express their operational intents without manual device configuration. LLMs offer promising capabilities in reasoning, planning, and task orchestration, enabling seamless automation of data retrieval, analysis, and workflow execution. This project aims to the second-round candidation of Concours Innovation Creative Challenge 2026 in the intersection domain between IOT, Intelligence Artificielle (AI) and Edge-Cloud Computing. Our complete work presents in [CICT Hackathon Round 2 Presentation](https://docs.google.com/presentation/d/1wKNIP_Rr-3uXvEWs3CL8ITc8lvj-x6bo/edit?slide=id.g3d121bd3dce_1_14#slide=id.g3d121bd3dce_1_14).

![Data Auto-Collection in IOT Smart Healthcare Systems](docs/general-architecture/architecture.png)

## Application Scenarios

### Scenario 1: Real-Time Physiological Monitoring
Wearable and implantable sensors continuously monitor vital signs (blood pressure, heart rate) with anomaly detection and immediate caregiver alerts.

**Research Direction:** Edge-based lightweight patient prediction models (distillation) running directly on sensor devices.

### Scenario 2: Smart Hospital BioIOT Management 
Camera-based monitoring systems detect resident falls, autonomous medical IOT sensors/actuators management, enhancing safety, performance, energy-awareness while reducing staff workload.

**Research Direction:** Generative AI multi-agent for task orchestration, deployment, auto-configuration, plan validation and execution.

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

# Activate environment (Poetry 2.x)
source $(poetry env info --path)/bin/activate

# Or for Poetry 1.x
poetry shell

```

---

## Project Structure

```
llm-intent-orchestration/
├── src/
│   ├── main.py              # CLI entry point in FastMCP server with menu interface
│   ├── crew.py              # Multi-agent orchestration
│   ├── agents/
│   │   └── agents.py        # LLM Agent logic (Gemini LLM)
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

### Running the Application

```bash
# Seed database mitigation (Future replacement with real-time iot device data)
python -m poetry run -m python src.db.main 

# Uvicorn App
python -m poetry run uvicorn src.main:app --host 0.0.0.0 --port 8001
```

---

## References

1. MCP SDK Integration: [modelcontextprotocol.io/docs/sdk](https://modelcontextprotocol.io/docs/sdk)
2. CrewAI Task Automation: [docs.crewai.com/en/mcp/overview](https://docs.crewai.com/en/mcp/overview)
3. CrewAI Tutorial: [youtu.be/sPzc6hMg7So](https://www.youtube.com/watch?v=sPzc6hMg7So)
4. MCP Learning Resources: [youtu.be/QIOk4XZ5XNU](https://youtu.be/QIOk4XZ5XNU)
5. CrewAI + FastMCP: [github.com/ashishpatel26/Crewai-MCP-Course](https://github.com/ashishpatel26/Crewai-MCP-Course)
6. Integration with FastMCP via [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
7. ONOS MCP Server (Code inspiration):[onos-mcp-server](https://github.com/MCP-Mirror/davidlin2k_onos-mcp-server)
