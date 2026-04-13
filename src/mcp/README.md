# MCP Agent Tools for Patient Health Monitoring in Medical IoT Environments

## Tools Structure

The MCP (Model Context Protocol) module provides agents and algorithms for intelligent intent management in medical IoT environments. Here's the folder organization:

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

### Component Overview

**Core Modules:**
- `main.py` - Orchestrates MCP integration with agent framework
- `deployment.py` - Tools for deployment monitoring and device management
- `plan_validation.py` - Tools for plan validation against requirements

**Algorithms Subfolder:**
- `naive.py` - Baseline sensor activation (all sensors active, used as reference)
- `cellulaire.py` - Zone-based sequential clustering for balanced coverage and energy
- `probabilistic.py` - Advanced energy-efficient activation using probability distribution and spatial coverage modeling

## 1.1 Edge Anomaly Detection Agent

---

## 1.2 Device Orchestration Agent

---

## 1.3 Plan Validation 
### 1.3.1 Naive Sensor Activation (Baseline)

This algorithm ensures continuous monitoring of the environment by keeping all sensor nodes fully active, without prioritization or contextual awareness. This baseline is used as a reference for evaluating optimized strategies.

### 1.3.2 Cellulaire Sequential Clustering Zone-based Activation

This algorithm enables monitoring coverage by activating nodes sequentially across space, reducing simultaneous energy usage.

### 1.3.3 Probabilistic & Spatially Optimized Activation (Energy-Efficient)

This algorithm minimizes energy by activating only necessary devices using the probability γ of patient egress [1] and spatial coverage (x, y, z, r) [7] using Python library.

> **Note:** More details of algorithm implementation in folder algorithms.

---
## 1.4 Deployment Monitoring Agent
