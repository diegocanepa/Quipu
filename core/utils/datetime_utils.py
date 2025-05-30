from datetime import datetime

def parse_datetime(dt_str: str) -> datetime:
    """
    Parse a datetime string with flexible microsecond precision.
    Handles both standard ISO format and non-standard microsecond precision.
    
    Args:
        dt_str (str): The datetime string to parse
        
    Returns:
        datetime: The parsed datetime object
        
    Examples:
        >>> parse_datetime("2025-05-18T22:31:56.08304+00:00")
        datetime(2025, 5, 18, 22, 31, 56, 83040)
        >>> parse_datetime("2025-05-18T22:31:56.083040+00:00")
        datetime(2025, 5, 18, 22, 31, 56, 83040)
    """
    try:
        # First try standard ISO format
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except ValueError:
        # If that fails, try to handle non-standard microsecond precision
        if '.' in dt_str:
            base, ms = dt_str.split('.')
            # Ensure microseconds have exactly 6 digits
            ms = ms.split('+')[0]  # Remove timezone if present
            ms = ms.ljust(6, '0')[:6]  # Pad or truncate to 6 digits
            dt_str = f"{base}.{ms}+00:00"
            return datetime.fromisoformat(dt_str)
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00')) 