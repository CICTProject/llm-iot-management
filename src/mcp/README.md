# MCP Agent Tools for Patient Health Monitoring in Medical IoT Environments

## Tools Structure

The MCP (Model Context Protocol) module provides agents and relevant algorithms for intelligent intent management in medical IoT environments. 

```
mcp/
├── __init__.py                          # Package initialization
├── main.py                              # Main entry point for MCP integration
├── deployment.py                        # Deployment monitoring agent tools
├── plan_validation.py                   # Plan validation agent tools
│
├── algorithms/                          # Optimization algorithms for plan validation
│   ├── __init__.py
│   ├── naive.py                        # Baseline (reference implementation)
│   ├── cellulaire.py                   # Sequential clustering zone-based activation
│   ├── probabilistic.py                # Energy-efficient probabilistic & spatial optimization
│   └── README.md                       # Algorithm details 
└── README.md                            # All agent tool explanations
```

## 1.1 Edge Anomaly Detection Agent

Detects anomalies in sensor data and device health by monitoring metric values against historical patterns and device status thresholds. Generates alerts when deviations exceed normal operating ranges.

---

## 1.2 Device Orchestration Agent

Converts medical staff intents into executable orchestration plans by selecting optimal devices, strategies, and activation sequences. Manages resource allocation and validates plans against system constraints.

---

## 1.3 Deployment Monitoring Agent

Monitors medical sensor deployments in real-time by querying device status, network topology, and health metrics from InfluxDB. Provides comprehensive system visibility and historical data analysis.

---
## 1.4 Plan Validation

Validates deployment plans and sensor activation strategies against system constraints and resource availability. Applies optimization algorithms to minimize energy or maximize coverage for user recommendations.

### 1.4.1 Naive Sensor Activation (Baseline)

Keeps all sensor nodes fully active without prioritization or contextual awareness. Provides maximum coverage with highest energy consumption. Used as reference baseline.

### 1.4.2 Cellulaire Sequential Clustering Zone-based Activation

Activates sensor nodes sequentially across spatial zones with clustering. Reduces simultaneous energy usage while maintaining monitoring coverage through sequential node activation.

### 1.4.3 Probabilistic & Spatially Optimized Activation (Energy-Efficient)

Minimizes energy consumption by activating only necessary devices using probability γ of patient egress and spatial coverage (x, y, z, r). Optimal for extended deployments with energy constraints.

> [!TIPS] Detailed algorithm implementation in [algorithms/README.md](algorithms/README.md).

---

## 1.5 Plan Execution

Translates orchestration plans into HTTP-executable instructions for IoT sensor networks. Asynchronous execution of different activation algorithms based on the orchestration plan and deployment status. Generates detailed execution plans with device details, services, and HTTP request actions for device activation.
