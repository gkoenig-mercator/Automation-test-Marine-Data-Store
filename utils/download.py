import os
import pandas as pd
import copernicusmarine
from typing import Optional


def determine_region(dataset_id: str, region_dict: dict) -> str:
    for region, meta in region_dict.items():
        if any(keyword in dataset_id for keyword in meta["keywords"]):
            return region
    return "Global"


def remove_files(directory: str):
    for filename in os.listdir(directory):
        if filename.endswith((".csv", ".nc")):
            os.remove(os.path.join(directory, filename))


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


class Downloader:
    def __init__(self, info: dict, region_dict: dict, data_dir: str):
        self.info = info
        self.region_dict = region_dict
        self.data_dir = data_dir
        self.temp_file_dir = os.path.join(data_dir, "temp/")
        
        # State
        self.downloadable = False
        self.last_downloadable_time = pd.NaT
        self.commands = [None, None, None]
        self.errors = [None, None, None]

    def _remove_temp_files(self):
        if os.path.exists(self.temp_file_dir):
            remove_files(self.temp_file_dir)

    def _attempt(self, index: int, kwargs: dict, command_repr: str):
        """Generic attempt handler"""
        try:
            self.commands[index] = command_repr
            copernicusmarine.subset(**kwargs)
            self._remove_temp_files()
            self.downloadable = True
            self.last_downloadable_time = self.info["last_available_time"]
            return True
        except Exception as e:
            self.errors[index] = str(e)
            return False

    def attempt_first(self):
        region = self.region_dict[self.info["region"]]
        kwargs = build_subset_kwargs(
            self.info, region, self.temp_file_dir, [self.info["variable_name"]]
        )
        command_repr = f"copernicusmarine.subset({kwargs})"
        return self._attempt(0, kwargs, command_repr)

    def attempt_second(self):
        region = self.region_dict[self.info["region"]]
        kwargs = build_subset_kwargs(self.info, region, self.temp_file_dir)
        command_repr = f"copernicusmarine.subset({kwargs})"
        return self._attempt(1, kwargs, command_repr)

    def attempt_third(self):
        start_time = pd.Timestamp(self.info["last_available_time"]) - pd.Timedelta(hours=1)
        kwargs = dict(
            dataset_id=self.info["dataset_id"],
            start_datetime=start_time.strftime("%Y-%m-%d %X"),
            end_datetime=self.info["last_available_time"],
            variables=[self.info["variable_name"]],
            output_directory=self.temp_file_dir,
            output_filename="test.nc",
            service=self.info["service_name"],
        )
        command_repr = (
            f"copernicusmarine.subset(dataset_id={kwargs['dataset_id']}, "
            f"start_datetime={kwargs['start_datetime']}, end_datetime={kwargs['end_datetime']}, "
            f"variables={kwargs['variables']}, output_directory={kwargs['output_directory']}, "
            f"output_filename={kwargs['output_filename']}, service={kwargs['service']})"
        )
        return self._attempt(2, kwargs, command_repr)

    def run(self):
        """Try all attempts in order"""
        for attempt in [self.attempt_first, self.attempt_second, self.attempt_third]:
            if attempt():
                break
        return {
            "downloadable": self.downloadable,
            "last_downloadable_time": self.last_downloadable_time,
            "commands": self.commands,
            "errors": self.errors,
        }
