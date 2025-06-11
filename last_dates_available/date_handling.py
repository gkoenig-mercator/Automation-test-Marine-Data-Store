from datetime import datetime, timedelta

def shift_date(date_str: str, days: int) -> str:
    """
    Shifts a given date string (YYYY-MM-DD HH:MM:SS±HH:MM) by a specified number of days
    and returns it in the format YYYY-MM-DDTHH:MM:SS.
    
    Args:
        date_str (str): The original date string in format YYYY-MM-DD HH:MM:SS±HH:MM.
        days (int): Number of days to shift (positive for future, negative for past).
    
    Returns:
        str: The new date string in the format YYYY-MM-DDTHH:MM:SS.
    """
    try:
        # Convert to datetime object (including timezone offset if present)
        date_obj = datetime.fromisoformat(date_str)
        
        # Shift the date
        new_date_obj = date_obj + timedelta(days=days)
        
        # Return in required format: "YYYY-MM-DDTHH:MM:SS"
        return new_date_obj.strftime("%Y-%m-%dT%H:%M:%S")
    except ValueError:
        raise ValueError("Invalid date format. Expected YYYY-MM-DD HH:MM:SS±HH:MM")


# Example usage
if __name__ == "__main__":
    test_date = "2025-02-01T15:30:45"
    print("Original:", test_date)
    print("One day before:", shift_date(test_date, -1))
    print("One day after:", shift_date(test_date, 1))
