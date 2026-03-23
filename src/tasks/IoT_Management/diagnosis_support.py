"""Diagnosis support task."""
from crewai import Task
from typing import Optional

# 4.7 Diagnosis Support for Doctors
def diagnosis_router(agent, patient_id: Optional[str] = None, sensor_data: Optional[dict] = None, patient_history: Optional[dict] = None):
    """Diagnosis support task for doctors.
    
    Args:
        agent: The CrewAI agent to execute this task
        patient_id: Patient identifier
        patient_history: Patient medical history
    """
    return Task(
        description=f"Analyze sensor data {sensor_data} and patient history {patient_history} for patient {patient_id} to support diagnosis.",
        expected_output="Diagnosis recommendations with treatment suggestions.",
        agent=agent
    )
