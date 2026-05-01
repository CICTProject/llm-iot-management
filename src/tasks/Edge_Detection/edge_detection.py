"""Edge LLM task for sensor data anomaly detection."""
from typing import Optional
from crewai import Task

# 4.6 Edge LLM Anomaly Detection (Giang's Task)
def edge_router(agent, sensor_id: Optional[str] = None, threshold: Optional[float] = None):
    """
    Edge LLM anomaly detection task.
    """
    sensor_desc = sensor_id or "environmental"
    threshold_desc = threshold or "predefined"
    return Task(
        description=f"Detect anomalies in sensor {sensor_desc} data with threshold {threshold_desc}.",
        expected_output="Anomaly detection report with alerts.",
        agent=agent
    )
