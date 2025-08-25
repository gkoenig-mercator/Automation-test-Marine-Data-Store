# tests/downloading_datasets.py
import pandas as pd
from io import StringIO
import pytest
from test_availability_data.downloading_datasets import assign_regions, process_row_for_download, read_input_csv, write_output_csv
from test_availability_data.utils.download import Downloader

class FakeDownloader:
    def __init__(self, data_dir):
        pass

    def run(self, attempts):
        return {
            "downloadable": True,
            "last_downloadable_time": "2023-01-01 01:00:00",
            "commands": ["cmd1", "cmd2", "cmd3"],
            "errors": [None, None, None],
        }

@pytest.fixture
def region_dict():
    return {
        "Europe": {"keywords": ["eu"],
                   "min_lon": -44,
                   "max_lon": -43,
                   "min_lat": -90,
                   "max_lat": -60,
                  },
        "Asia": {"keywords": ["asia"],
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
            "chlorophyll_global"
        ],
        "dataset_version": [
            "202211",
            "202211",
            "202211"]
        ,
        "version_part": [
            "default",
            "default",
            "default"],
        "service_name": [
            "arco-geo-series",
            "arco-time-series",
            "arco-time-series"],
        "variable_name":
        ["temperature",
         "chl",
         "bottomT"],
        "has_time_coordinate":
        [True,
         True,
         True],
        "last_available_time":
        ["2025-08-30 00:00:00",
         None,
         "2025-08-30 00:00:00"]
    }
    return pd.DataFrame(data)

def test_assign_regions(sample_df, region_dict):

    df = assign_regions(sample_df.copy(), region_dict)

    assert "region" in df.columns
    # Example: if dataset_id has "eu", region should be Europe
    assert all(df.loc[df["dataset_id"].str.contains("eu"), "region"] == "Europe")
    assert all(df.loc[df["dataset_id"].str.contains("asia"), "region"] == "Asia")

def test_process_row_for_download(sample_df, region_dict):
    row = sample_df.iloc[0]

    result = process_row_for_download(
        row, data_dir=".", region_identifier=region_dict, downloader_cls=FakeDownloader
    )

    assert result["downloadable"] is True
    assert result["first_command"] == "cmd1"
    assert result["first_error"] is None

def test_process_row_missing_time(sample_df, region_dict):
    row = sample_df.iloc[1]  # last_available_time is None
    result = process_row_for_download(row, data_dir=".", region_identifier=region_dict)
    assert result["downloadable"] is False
    assert result["first_error"] == "No last_available_time available"