from datetime import datetime


def format_timestamp(timestamp):
    """
    Formats a timestamp string into a human-readable date and time
    """
    if not timestamp:
        return "-"

    try:
        # Try parsing the timestamp
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        # Format it as a readable string
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, AttributeError):
        # Return the original value if parsing fails
        return timestamp
