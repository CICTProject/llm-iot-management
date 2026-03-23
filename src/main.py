"""FastMCP Server for IoT Orchestration."""
from fastmcp import FastMCP
from crew.crew import CustomCrew

# Initialize MCP server
mcp = FastMCP("IoT Orchestration MCP Server")
custom_crew = CustomCrew()


@mcp.tool()
def run_all_agents() -> str:
    """Run all IoT orchestration agents."""
    result = custom_crew.run_all()
    return str(result)


@mcp.tool()
def run_security_agent() -> str:
    """Run security and credentials monitoring agent."""
    result = custom_crew.run_security()
    return str(result)


@mcp.tool()
def run_deployment_agent() -> str:
    """Run deployment monitoring agent."""
    result = custom_crew.run_deployment()
    return str(result)


@mcp.tool()
def run_orchestration_agent() -> str:
    """Run device orchestration agent."""
    result = custom_crew.run_orchestration()
    return str(result)


@mcp.tool()
def run_network_agent() -> str:
    """Run network auto-configuration agent."""
    result = custom_crew.run_network()
    return str(result)


@mcp.tool()
def run_diagnosis_agent() -> str:
    """Run diagnosis support agent."""
    result = custom_crew.run_diagnosis()
    return str(result)


if __name__ == "__main__":
    mcp.run()
