# Multi Agent for Patient Health Monitoring Tasks in Medical IoT

AI Agent task definitions for intelligent intent management in medical IoT environments.

```
tasks/
├── edge_detection/              # Health anomaly detection
│   ├── edge_detection.py       # Anomaly classification
│   ├── edge_inference.py       # Real-time inference
│   ├── cloud_model.pkl         # Pre-trained ML model
│   └── README.md               # Implementation details
│
└── system_management/           # IoT orchestration and monitoring
    ├── deployment_monitoring.py # Monitor device deployment status
    ├── device_orchestration.py  # Create and manage activation plans
    ├── plan_validation.py       # Validate plans against constraints
    ├── plan_execution.py        # Execute orchestration plans
    └── __init__.py
```

## 1.1 Edge Detection Task

Detects health anomalies in sensor readings using on-device AI models. Analyzes vital signs (blood pressure, heart rate, temperature) and alerts medical staff when readings exceed normal ranges. Preserves privacy by running inference locally on sensors and only transmitting alerts.

---

## 1.2 Deployment Monitoring Task

Monitors IoT device deployment status in real-time. Queries device health, network topology, and connectivity from InfluxDB. Provides system visibility for nurses and medical staff.

---

## 1.3 Device Orchestration Task

Converts medical staff intents into executable orchestration plans. Selects optimal devices, activation strategies, and sequences. Manages resource allocation and validates plans against system constraints.

---

## 1.4 Plan Validation Task

Validates deployment plans against system requirements and resource availability. Applies optimization algorithms (naive, sequential, probabilistic) to meet user constraints for coverage or energy efficiency.

---

## 1.5 Plan Execution Task

Translates validated orchestration plans into HTTP-executable instructions for IoT devices. Generates device activation sequences with HTTP request templates ready for execution.

---

## Integration: Multiple AI Agent Management 

Each task returns a CrewAI `Task` object configured with:
- Description of the task objective
- Expected output format
- Associated MCP tool (deployment, orchestration, validation, or execution)
- Agent to execute the task

Tasks are invoked via router functions that accept agent and optional parameters (plan_id, requirements, device filters).

> [!NOTE]
> See [mcp/README.md](../mcp/README.md) for detailed tool documentation.
