import re
import argparse
import os
from typing import Optional, Generator, Tuple
from copernicusmarine import CopernicusMarineVariable, CopernicusMarineService


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
        if coordinate.coordinate_id == "time":
            if coordinate.maximum_value:
                return coordinate.maximum_value
            else:
                return coordinate.values[-1]

    return None


def filter_allowed_services(
    services: list[CopernicusMarineService],
    allowed_services: Optional[list[str]] = None,
) -> Generator[CopernicusMarineService, None, None]:
    """Yield services in the authorized list"""
    for service in services:
        if service.service_name not in allowed_services:
            continue
        else:
            yield service


def check_if_there_is_time_coordinate(
    variables: list[CopernicusMarineVariable],
) -> bool:
    """Check if the variables have the "time" coordinate"""

    return any(
        coord.coordinate_id == "time" for var in variables for coord in var.coordinates
    )


def get_first_variable_with_a_time_coordinate(
    variables: list[CopernicusMarineVariable],
) -> Tuple[Optional[str], Optional[int]]:
    """Get the first variable that has a time coordinate"""
    index = 0
    for index, variable in enumerate(variables):
        for coordinate in variable.coordinates:
            if coordinate.coordinate_id == "time":
                return variable.short_name, index
    return None, None


def get_data_directory_from_command_line():
    parser = argparse.ArgumentParser(
        description="Analyze dataset downloadability and timing."
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        required=True,
        help="Path to the directory containing csv files",
    )
    args = parser.parse_args()
    return args.data_dir

def get_duration_in_seconds_from_two_utc(start_time, end_time):
    duration = end_time - start_time

    duration_seconds = duration.total_seconds()

    return int(duration_seconds)

def get_number_of_datasets_downloaded(data_dir, filename="downloaded_datasets.csv"):
    file_path = os.path.join(data_dir, filename)
    with open(file_path, "r", encoding="utf-8") as f:
         num_rows = sum(1 for _ in f) - 1 

    return num_rows
