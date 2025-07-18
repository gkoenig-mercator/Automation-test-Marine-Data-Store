import copernicusmarine
import re
from typing import Optional, Generator, Tuple
from copernicusmarine import CopernicusMarineVariable,CopernicusMarineService

# We need this function in case the datasets are not available at the good date
def extract_last_date(string_with_last_available_date: str) -> Optional[str]:
    """Look for the date in an expression returned via its format YYYY-MM-DD,
        here it is the last of a list."""
    
    last_date_pattern = r"\[.*?, (\d{4}-\d{2}-\d{2})"
    matches = re.findall(last_date_pattern, string_with_last_available_date)
    return matches[-1] if matches else None

def extract_last_available_time(variable: CopernicusMarineVariable) -> Optional[float]:
    """Get the last available from the metadata returned by copernicusmarine.describe"""

    for coordinate in variable.coordinates:
        if  coordinate.coordinate_id == 'time':
            if coordinate.maximum_value:
                return coordinate.maximum_value or coordinate.values[-1]

    return None

def filter_allowed_services(services: list[CopernicusMarineService],
                            allowed_services: Optional[list[str]] = None
                           ) -> Generator[CopernicusMarineService, None, None]:
    """Yield services in the authorized list"""
    for service in services:
        if service.service_name not in allowed_services:
            continue
        else:
            yield service

def check_if_there_is_time_coordinate(variables: list[CopernicusMarineVariable]
                                     ) -> bool:
    """Check if the variables have the "time" coordinate"""

    return any(
        coord.coordinate_id == 'time'
        for var in variables
        for coord in var.coordinates
    )

def get_first_variable_with_a_time_coordinate(variables: list[CopernicusMarineVariable]
                                             ) -> Tuple[Optional[str], Optional[int]]:
    """Get the first variable that has a time coordinate"""
    variable_with_time_coordinate = None
    index = 0
    for index, variable in enumerate(variables):
        for coordinate in variable.coordinates:
            if coordinate.coordinate_id == 'time':
                return variable.short_name, index
    return None, None
