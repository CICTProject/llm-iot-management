import logging
import json
from datetime import datetime
from typing import Any, Dict, List

from . import mcp_server
from src.db.database import get_db_client

from src.utils.system import (
    query_deployment_status,
)

logger = logging.getLogger(__name__)

@mcp_server.tool(name="get_deployment_status")
async def get_deployment_status() -> Dict[str, Any]:
    """Get current deployment status for plan validation."""
    try:
        deployment_status = query_deployment_status()
        logger.info("Queried deployment status for validation")
        return deployment_status
    except Exception as e:
        logger.error(f"Failed to query deployment status for validation: {e}")
        return {"error": str(e)}
