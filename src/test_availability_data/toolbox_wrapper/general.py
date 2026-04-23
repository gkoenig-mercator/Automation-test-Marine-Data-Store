import re
from typing import Optional

from copernicusmarine import CopernicusMarineService, CopernicusMarineVariable


def extract_last_date(string_with_last_available_date: str) -> Optional[str]:
    """Look for the last date in a string, expected format YYYY-MM-DD."""
    last_date_pattern = r"\[.*?, (\d{4}-\d{2}-\d{2})"
    matches = re.findall(last_date_pattern, string_with_last_available_date)
    return matches[-1] if matches else None


def extract_last_available_time(variable: CopernicusMarineVariable) -> Optional[float]:
    """Get the last available time from copernicusmarine variable metadata."""
    for coordinate in variable.coordinates:
        if coordinate.coordinate_id == "time":
            if coordinate.maximum_value:
                return float(coordinate.maximum_value)
            if coordinate.values:
                return float(coordinate.values[-1])
    return None


def filter_allowed_services(
    services: list[CopernicusMarineService],
    allowed_services: Optional[list[str]] = None,
) -> list[CopernicusMarineService]:
    """Return services that are in the allowed list, or all services if no filter is given."""
    if allowed_services is None:
        return services
    return [s for s in services if s.service_name in allowed_services]


def check_if_there_is_time_coordinate(
    variables: list[CopernicusMarineVariable],
) -> bool:
    """Check if any variable has a time coordinate."""
    return any(
        coord.coordinate_id == "time" for var in variables for coord in var.coordinates
    )


def get_first_variable_with_a_time_coordinate(
    variables: list[CopernicusMarineVariable],
) -> tuple[Optional[str], Optional[int]]:
    """Get the name and index of the first variable that has a time coordinate."""
    for index, variable in enumerate(variables):
        for coordinate in variable.coordinates:
            if coordinate.coordinate_id == "time":
                return variable.short_name, index
    return None, None
