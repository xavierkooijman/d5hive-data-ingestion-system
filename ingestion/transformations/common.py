import logging
logger = logging.getLogger(__name__)


def ms_to_kmh(value: float) -> float:
    """ Convert speed from meters per second to kilometers per hour.
        Args:
            value (float): Speed in meters per second.
        Returns:
            float: Speed in kilometers per hour, or None if input is None.
    """
    return value * 3.6 if value is not None else None


def wind_direction_to_degrees(value: str) -> int | None:
    """Convert cardinal wind direction to degrees. Returns None for invalid input.
    Args:        
        value (str): Cardinal wind direction (e.g., 'N', 'NE', 'E', etc.)
    Returns:     
        int or None: Wind direction in degrees (0-360) or None if input is invalid
    """
    directions = {
        "N": 0,
        "NE": 45,
        "E": 90,
        "SE": 135,
        "S": 180,
        "SW": 225,
        "W": 270,
        "NW": 315,
    }
    if value is not None and value in directions:
        return directions[value]
    else:
        logger.warning(f"Invalid wind direction value: {value}")
        return None
