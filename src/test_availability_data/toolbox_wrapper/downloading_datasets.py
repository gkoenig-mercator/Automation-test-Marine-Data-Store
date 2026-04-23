import logging
import os
import uuid

import pandas as pd

from test_availability_data.toolbox_wrapper.download import Downloader
from test_availability_data.utils.miscellaneous import determine_region

logging.getLogger("copernicusmarine").setLevel("INFO")


class DatasetAvailabilityChecker:
    def __init__(
        self,
        data_dir: str,
        region_dict: dict,
        input_filename: str = "list_of_informations_from_the_describe.csv",
        downloader_cls=Downloader,
    ):
        self.data_dir = data_dir
        self.region_dict = region_dict
        self.input_filename = input_filename
        self.downloader_cls = downloader_cls

    def run(self) -> pd.DataFrame:
        df = self._read_input_csv()
        df = self._assign_regions(df)
        df = self._process_dataframe(df)
        df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]
        return df

    def _read_input_csv(self) -> pd.DataFrame:
        path = os.path.join(self.data_dir, self.input_filename)
        return pd.read_csv(path)

    def _assign_regions(self, df: pd.DataFrame) -> pd.DataFrame:
        df["region"] = df["dataset_id"].apply(
            lambda ds: determine_region(ds, self.region_dict)
        )
        return df

    def _process_row(self, row: pd.Series) -> dict:
        if pd.isnull(row["last_available_time"]):
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

        downloader = self.downloader_cls(row.to_dict(), self.region_dict, self.data_dir)
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

    def _process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        results = df.apply(self._process_row, axis=1, result_type="expand")
        return pd.concat([df, results], axis=1)
