"""Network auto-configuration task."""
from typing import Optional
from crewai import Task

# 4.5 Network Auto-Configuration
def network_config_router(agent, src_ip: Optional[str] = None, dst_ip: Optional[str] = None, src_port: Optional[int] = None, dst_port: Optional[int] = None, action: Optional[str] = None):
    """Auto-configure network for IoT devices.
    
    Args:
        agent: The CrewAI agent to execute this task
        src_ip: Source IP address
        dst_ip: Destination IP address
        src_port: Source port number
        dst_port: Destination port number
        action: SDN flow action (allow/deny/forward)
    """
    return Task(
        description=f"Auto-configure network flow: {src_ip}:{src_port} -> {dst_ip}:{dst_port} action={action}.",
        expected_output="SDN flow data with IPs, ports, and actions.",
        agent=agent
    )
