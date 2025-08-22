import os
import pandas as pd
import copernicusmarine
from typing import Optional


def determine_region(dataset_id: str, region_dict: dict) -> str:
    for region, meta in region_dict.items():
        if any(keyword in dataset_id for keyword in meta["keywords"]):
            return region
    return "Global"

def build_subset_kwargs(
    info: dict,
    region: dict,
    data_dir: str,
    variables: Optional[list[str]] = None,
    maximum_depth: Optional[float] = 5,
):
    start_time = pd.Timestamp(info["last_available_time"]) - pd.Timedelta(hours=1)
    return {
        "dataset_id": info["dataset_id"],
        "start_datetime": start_time.strftime("%Y-%m-%d %X"),
        "end_datetime": info["last_available_time"],
        "output_directory": data_dir,
        "output_filename": "test.nc",
        "maximum_depth": maximum_depth,
        "minimum_longitude": region["min_lon"],
        "maximum_longitude": region["max_lon"],
        "minimum_latitude": region["min_lat"],
        "maximum_latitude": region["max_lat"],
        "service": info["service_name"],
        **({"variables": variables} if variables else {}),
    }

def build_attempts(info: dict, region_dict: dict, data_dir: str) -> list[dict]:
    temp_file_dir = os.path.join(data_dir, "temp/")
    region = region_dict.get(info.get("region"))

    attempts = []

    # Attempt 1: single variable
    if region:
        kwargs1 = build_subset_kwargs(info, region, temp_file_dir, [info["variable_name"]])
        attempts.append({
            "kwargs": kwargs1,
            "command_repr": f"copernicusmarine.subset({kwargs1})"
        })

    # Attempt 2: all variables
    if region:
        kwargs2 = build_subset_kwargs(info, region, temp_file_dir)
        attempts.append({
            "kwargs": kwargs2,
            "command_repr": f"copernicusmarine.subset(all variables: {kwargs2})"
        })

    # Attempt 3: no region info
    start_time = pd.Timestamp(info["last_available_time"]) - pd.Timedelta(hours=1)
    kwargs3 = {
        "dataset_id": info["dataset_id"],
        "start_datetime": start_time.strftime("%Y-%m-%d %X"),
        "end_datetime": info["last_available_time"],
        "variables": [info["variable_name"]],
        "output_directory": temp_file_dir,
        "output_filename": "test.nc",
        "service": info["service_name"],
    }
    attempts.append({
        "kwargs": kwargs3,
        "command_repr": f"copernicusmarine.subset(no region info: {kwargs3})"
    })

    return attempts

class Downloader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.temp_file_dir = os.path.join(data_dir, "temp/")
        self.downloadable = False
        self.last_downloadable_time = pd.NaT
        self.commands = []
        self.errors = []

    def _remove_temp_files(self):
        if os.path.exists(self.temp_file_dir):
            remove_files(self.temp_file_dir)

    def run(self, attempts: list[dict]):
        """
        Executes a list of attempts.
        Each attempt is a dict with keys:
            - 'kwargs': dict for copernicusmarine.subset
            - 'command_repr': string describing the command
        """
        self.commands = [None] * len(attempts)
        self.errors = [None] * len(attempts)

        for i, attempt in enumerate(attempts):
            try:
                self.commands[i] = attempt['command_repr']
                copernicusmarine.subset(**attempt['kwargs'])
                self._remove_temp_files()
                self.downloadable = True
                self.last_downloadable_time = attempt['kwargs'].get('end_datetime', pd.NaT)
                break
            except Exception as e:
                self.errors[i] = str(e)

        return {
            "downloadable": self.downloadable,
            "last_downloadable_time": self.last_downloadable_time,
            "commands": self.commands,
            "errors": self.errors,
        }
