"""
Energy-related utility functions for plan validation and grid analysis.
"""

import logging
from typing import List

from src.db.database import get_db_client

logger = logging.getLogger(__name__)

# Cache for peak hours calculation
_PEAK_HOURS = []
_PEAK_HOURS_CALCULATED = False


def calculate_peak_hours_from_db() -> List[int]:
    """Calculate peak load hours from InfluxDB historical data.
    
    Queries the energy_consumption bucket for peak_load_hour field values
    and returns hours (0-23) when peak load is detected.
    
    Returns:
        List of hours (0-23) identified as peak load hours.
        Falls back to 9am-5pm (9-17) if data unavailable.
    """
    global _PEAK_HOURS, _PEAK_HOURS_CALCULATED
    
    if _PEAK_HOURS_CALCULATED:
        return _PEAK_HOURS
    
    try:
        db_client = get_db_client()
        query_api = db_client.get_query_client()
        
        # Query peak load hour data from last 7 days
        query = '''
        from(bucket: "energy_consumption")
          |> range(start: -7d)
          |> filter(fn: (r) => r["_measurement"] == "grid_metrics")
          |> filter(fn: (r) => r["_field"] == "peak_load_hour")
        '''
        
        result = query_api.query(query)
        
        peak_hours_set = set()
        for table in result:
            for record in table.records:
                if record.value == 1:
                    hour = record.get_time().hour
                    peak_hours_set.add(hour)
        
        _PEAK_HOURS = sorted(list(peak_hours_set))
        _PEAK_HOURS_CALCULATED = True
        logger.info(f"Calculated peak hours from InfluxDB: {_PEAK_HOURS}")
        
    except Exception as e:
        logger.warning(f"Could not calculate peak hours from InfluxDB: {e}. Using default.")
        _PEAK_HOURS = list(range(9, 18))  # Default: 9am to 5pm
        _PEAK_HOURS_CALCULATED = True
    
    return _PEAK_HOURS


def reset_peak_hours_cache() -> None:
    """Reset the peak hours cache to force recalculation on next call.
    
    Useful after updating energy data in InfluxDB.
    """
    global _PEAK_HOURS_CALCULATED
    _PEAK_HOURS_CALCULATED = False
