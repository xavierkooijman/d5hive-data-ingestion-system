from datetime import datetime, timezone
import zoneinfo


def normalize_string_timestamp(timestamp: str, tz: str) -> datetime:
    """
    Convert a local timestamp string to UTC ISO 8601.

    Args:
        timestamp: "2026-05-23T18:30" or "2026-05-23T18:30:00"
        tz: IANA timezone string e.g. "Europe/Lisbon"

    Returns:
        datetime: timezone-aware UTC datetime e.g. datetime(2026, 5, 23, 17, 30, tzinfo=timezone.utc)
    """

    if "T" in timestamp and len(timestamp) == 16:
        timestamp += ":00"

    local_timezone = zoneinfo.ZoneInfo(tz)
    dt = datetime.fromisoformat(timestamp).replace(tzinfo=local_timezone)
    return dt.astimezone(timezone.utc)


def normalize_unix_timestamp(unix_timestamp: float | int) -> datetime:
    """
    Convert a Unix timestamp (int/float, always UTC) to UTC ISO 8601 datetime object.

    Args:
        unix_timestamp (float | int): Unix timestamp as int or float e.g. 1711411800
    Returns:
        datetime: timezone-aware UTC datetime e.g. datetime(2026, 5, 23, 17, 30, tzinfo=timezone.utc)
    """

    return datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
