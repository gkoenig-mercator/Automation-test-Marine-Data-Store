from datetime import datetime, timedelta

def shift_date(date_str: str, days: int) -> str:
    """
    Shifts a given date string (YYYY-MM-DDTHH:MM:SS) by a specified number of days.
    
    Args:
        date_str (str): The original date string in format YYYY-MM-DDTHH:MM:SS.
        days (int): Number of days to shift (positive for future, negative for past).
    
    Returns:
        str: The new date string in the same format.
    """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        new_date_obj = date_obj + timedelta(days=days)
        return new_date_obj.strftime("%Y-%m-%dT%H:%M:%S")
    except ValueError:
        raise ValueError("Invalid date format. Expected YYYY-MM-DDTHH:MM:SS")

# Example usage
if __name__ == "__main__":
    test_date = "2025-02-01T15:30:45"
    print("Original:", test_date)
    print("One day before:", shift_date(test_date, -1))
    print("One day after:", shift_date(test_date, 1))
