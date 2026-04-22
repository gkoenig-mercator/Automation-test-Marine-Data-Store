import os
from typing import Optional

import copernicusmarine
import pandas as pd


def determine_region(dataset_id: str, region_dict: dict) -> str:
    for region, meta in region_dict.items():
        if any(keyword in dataset_id for keyword in meta["keywords"]):
            return region
    return "Global"


def remove_files(directory: str):
    for filename in os.listdir(directory):
        if filename.endswith((".csv", ".nc")):
            os.remove(os.path.join(directory, filename))


class AttemptBuilder:
    def __init__(self, info: dict, region_dict: dict, data_dir: str):
        self.info = info
        self.region_dict = region_dict
        self.temp_file_dir = os.path.join(data_dir, "temp/")

    def _build_subset_kwargs(
        self,
        region: Optional[dict] = None,
        variables: Optional[list[str]] = None,
        maximum_depth: Optional[float] = 5,
    ) -> dict:
        start_time = pd.Timestamp(self.info["last_available_time"]) - pd.Timedelta(hours=1)
        return {
            "dataset_id": self.info["dataset_id"],
            "start_datetime": start_time.strftime("%Y-%m-%d %X"),
            "end_datetime": self.info["last_available_time"],
            "output_directory": self.temp_file_dir,
            "output_filename": "test.nc",
            "maximum_depth": maximum_depth,
            "service": self.info["service_name"],
            **({"variables": variables} if variables else {}),
            **(
                {
                    "minimum_longitude": region["min_lon"],
                    "maximum_longitude": region["max_lon"],
                    "minimum_latitude": region["min_lat"],
                    "maximum_latitude": region["max_lat"],
                }
                if region is not None
                else {}
            ),
        }

    def _build_command(self, kwargs: dict) -> str:
        args = ", ".join(f"{key}={value!r}" for key, value in kwargs.items())
        return f"copernicusmarine.subset({args})"

    def build(self) -> list[dict]:
        region = self.region_dict.get(self.info.get("region"))
        variable = [self.info["variable_name"]]

        attempt_configs = [
            {"region": region, "variables": variable},
            {"region": region, "variables": None},
            {"region": None,   "variables": variable},
        ]

        if not region:
            attempt_configs = [c for c in attempt_configs if c["region"] is None]

        attempts = []
        for config in attempt_configs:
            kwargs = self._build_subset_kwargs(
                region=config["region"], variables=config["variables"]
            )
            attempts.append({"kwargs": kwargs, "command_repr": self._build_command(kwargs)})

        return attempts


class Downloader:
    def __init__(self, info: dict, region_dict: dict, data_dir: str):
        self.data_dir = data_dir
        self.temp_file_dir = os.path.join(data_dir, "temp/")
        self.builder = AttemptBuilder(info, region_dict, data_dir)
        self.downloadable = False
        self.last_downloadable_time = pd.NaT
        self.commands = []
        self.errors = []

    def _remove_temp_files(self):
        if os.path.exists(self.temp_file_dir):
            remove_files(self.temp_file_dir)

    def run(self) -> dict:
        attempts = self.builder.build()
        self.commands: list[str | None] = [None] * len(attempts)
        self.errors: list[str | None] = [None] * len(attempts)

        for i, attempt in enumerate(attempts):
            try:
                self.commands[i] = attempt["command_repr"]
                copernicusmarine.subset(**attempt["kwargs"])
                self._remove_temp_files()
                self.downloadable = True
                self.last_downloadable_time = attempt["kwargs"].get("end_datetime", pd.NaT)
                break
            except Exception as e:
                self.errors[i] = str(e)

        return {
            "downloadable": self.downloadable,
            "last_downloadable_time": self.last_downloadable_time,
            "commands": self.commands,
            "errors": self.errors,
        }
