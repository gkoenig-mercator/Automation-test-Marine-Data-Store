# tests/test_downloading_datasets.py
import os

import pandas as pd
import pytest

from test_availability_data.toolbox_wrapper.download import Downloader
from test_availability_data.toolbox_wrapper.downloading_datasets import (
    DatasetAvailabilityChecker,
)

os.environ["COPERNICUSMARINE_USERNAME"] = "fake_user"
os.environ["COPERNICUSMARINE_PASSWORD"] = "fake_password"
os.environ["DATABASE_URL"] = "dummy_database_url"


class FakeDownloader(Downloader):
    def __init__(self, row_dict, region_dict, data_dir):
        pass

    def run(self):
        return {
            "downloadable": True,
            "last_downloadable_time": "2023-01-01 01:00:00",
            "commands": ["cmd1", "cmd2", "cmd3"],
            "errors": [None, None, None],
        }


@pytest.fixture
def region_dict():
    return {
        "Europe": {
            "keywords": ["eu"],
            "min_lon": -44,
            "max_lon": -43,
            "min_lat": -90,
            "max_lat": -60,
        },
        "Asia": {
            "keywords": ["asia"],
            "min_lon": 28,
            "max_lon": 29,
            "min_lat": 40,
            "max_lat": 41,
        },
    }


@pytest.fixture
def sample_df():
    data = {
        "dataset_id": [
            "temperature_eu_2021",
            "salinity_asia_2020",
            "chlorophyll_global",
        ],
        "dataset_version": ["202211", "202211", "202211"],
        "version_part": ["default", "default", "default"],
        "service_name": ["arco-geo-series", "arco-time-series", "arco-time-series"],
        "variable_name": ["temperature", "chl", "bottomT"],
        "has_time_coordinate": [True, True, True],
        "last_available_time": ["2025-08-30 00:00:00", None, "2025-08-30 00:00:00"],
    }
    return pd.DataFrame(data)


def test_assign_regions(sample_df, region_dict):
    checker = DatasetAvailabilityChecker(data_dir=".", region_dict=region_dict)
    df = checker._assign_regions(sample_df.copy())

    assert "region" in df.columns
    assert all(df.loc[df["dataset_id"].str.contains("eu"), "region"] == "Europe")
    assert all(df.loc[df["dataset_id"].str.contains("asia"), "region"] == "Asia")
    assert all(df.loc[df["dataset_id"].str.contains("global"), "region"] == "Global")


def test_process_row_for_download(sample_df, region_dict):
    checker = DatasetAvailabilityChecker(
        data_dir=".", region_dict=region_dict, downloader_cls=FakeDownloader
    )
    row = sample_df.iloc[0]  # temperature_eu_2021, has last_available_time
    result = checker._process_row(row)

    assert result["downloadable"] is True
    assert result["first_command"] == "cmd1"
    assert result["first_error"] is None
    assert result["second_command"] == "cmd2"
    assert result["third_command"] == "cmd3"


def test_process_row_missing_time(sample_df, region_dict):
    checker = DatasetAvailabilityChecker(data_dir=".", region_dict=region_dict)
    row = sample_df.iloc[1]  # salinity_asia_2020, last_available_time is None
    result = checker._process_row(row)

    assert result["downloadable"] is False
    assert result["first_error"] == "No last_available_time available"
    assert result["first_command"] is None
