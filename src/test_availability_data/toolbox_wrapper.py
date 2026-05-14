import os
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count

import copernicusmarine
import pandas as pd

from test_availability_data.config import logger
from test_availability_data.environment_variables import (
    COPERNICUSMARINE_SERVICE_PASSWORD,
    COPERNICUSMARINE_SERVICE_USERNAME,
)


def determine_region(dataset_id: str, region_dict: dict) -> str:
    for region, meta in region_dict.items():
        if any(keyword in dataset_id for keyword in meta["keywords"]):
            return region
    return "Global"


class AttemptBuilder:
    def __init__(self, info: dict, region_dict: dict, data_dir: str):
        self.info = info
        self.region_dict = region_dict
        self.temp_file_dir = os.path.join(data_dir, "temp/")

    def _build_subset_kwargs(
        self,
        region: dict | None = None,
        variables: list[str] | None = None,
        maximum_depth: float | None = 5,
    ) -> dict:
        start_time = pd.Timestamp(self.info["last_available_time"]) - pd.Timedelta(
            hours=1
        )
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
            {"region": None, "variables": variable},
        ]

        if not region:
            attempt_configs = [c for c in attempt_configs if c["region"] is None]

        attempts = []
        for config in attempt_configs:
            kwargs = self._build_subset_kwargs(
                region=config["region"], variables=config["variables"]
            )
            attempts.append(
                {"kwargs": kwargs, "command_repr": self._build_command(kwargs)}
            )

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

    def remove_files(self):
        if os.path.exists(self.temp_file_dir):
            for filename in os.listdir(self.temp_file_dir):
                if filename.endswith((".csv", ".nc")):
                    os.remove(os.path.join(self.temp_file_dir, filename))

    def _remove_temp_files(self):
        self.remove_files()

    def run(self) -> dict:
        attempts = self.builder.build()
        self.commands: list[str | None] = [None] * len(attempts)
        self.errors: list[str | None] = [None] * len(attempts)

        for i, attempt in enumerate(attempts):
            try:
                self.commands[i] = attempt["command_repr"]
                copernicusmarine.subset(
                    **attempt["kwargs"],
                    username=COPERNICUSMARINE_SERVICE_USERNAME,
                    password=COPERNICUSMARINE_SERVICE_PASSWORD,
                )
                self._remove_temp_files()
                self.downloadable = True
                self.last_downloadable_time = attempt["kwargs"].get(
                    "end_datetime", pd.NaT
                )
                break
            except Exception as e:
                self.errors[i] = str(e)

        return {
            "downloadable": self.downloadable,
            "last_downloadable_time": self.last_downloadable_time,
            "commands": self.commands,
            "errors": self.errors,
        }


def _process_row(
    row_dict: dict, region_dict: dict, data_dir: str, worker_id: int
) -> dict:
    """Module-level function for multiprocessing compatibility."""
    logger.info(
        f"Worker {worker_id} processing dataset {row_dict['dataset_id']} "
        f"with service {row_dict['service_name']}"
    )
    if pd.isnull(row_dict.get("last_available_time")):
        return {
            "downloadable": False,
            "last_downloadable_time": pd.NaT,
            "first_command": None,
            "first_error": "No last_available_time available",
            "second_command": None,
            "second_error": None,
            "third_command": None,
            "third_error": None,
        }

    # Each worker uses its own temp directory to avoid file conflicts
    worker_data_dir = os.path.join(data_dir, f"worker_{worker_id}")
    os.makedirs(os.path.join(worker_data_dir, "temp"), exist_ok=True)

    downloader = Downloader(row_dict, region_dict, worker_data_dir)
    result = downloader.run()

    return {
        "downloadable": result["downloadable"],
        "last_downloadable_time": result["last_downloadable_time"],
        "first_command": result["commands"][0],
        "first_error": result["errors"][0],
        "second_command": (
            result["commands"][1] if len(result["commands"]) > 1 else None
        ),
        "second_error": result["errors"][1] if len(result["errors"]) > 1 else None,
        "third_command": (
            result["commands"][2] if len(result["commands"]) > 2 else None
        ),
        "third_error": result["errors"][2] if len(result["errors"]) > 2 else None,
    }


class DatasetAvailabilityChecker:
    def __init__(
        self,
        data_dir: str,
        region_dict: dict,
        input_filename: str = "list_of_informations_from_the_describe.csv",
    ):
        self.data_dir = data_dir
        self.region_dict = region_dict
        self.input_filename = input_filename

    def run(self) -> pd.DataFrame:
        df = self._read_input_csv()
        df = self._assign_regions(df)
        df = self._process_dataframe(df)
        df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]
        self._cleanup_worker_dirs()
        return df

    def _read_input_csv(self) -> pd.DataFrame:
        path = os.path.join(self.data_dir, self.input_filename)
        return pd.read_csv(path)

    def _assign_regions(self, df: pd.DataFrame) -> pd.DataFrame:
        df["region"] = df["dataset_id"].apply(
            lambda ds: determine_region(ds, self.region_dict)
        )
        return df

    def _process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        rows = df.to_dict(orient="records")
        n_workers = min(cpu_count(), len(rows)) or 1
        results = [None] * len(rows)

        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            futures = {
                executor.submit(
                    _process_row,
                    row,
                    self.region_dict,
                    self.data_dir,
                    i % n_workers,
                ): i
                for i, row in enumerate(rows)
            }
            for future in as_completed(futures):
                idx = futures[future]
                results[idx] = future.result()

        results_df = pd.DataFrame(results)
        return pd.concat([df.reset_index(drop=True), results_df], axis=1)

    def _cleanup_worker_dirs(self):
        """Remove temporary worker directories after processing."""
        import shutil

        for name in os.listdir(self.data_dir):
            if name.startswith("worker_"):
                shutil.rmtree(os.path.join(self.data_dir, name), ignore_errors=True)
