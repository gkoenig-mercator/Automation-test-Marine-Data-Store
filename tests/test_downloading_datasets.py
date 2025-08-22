# tests/downloading_datasets.py
import pandas as pd
from io import StringIO
from test_availability_data.downloading_datasets import assign_regions, process_row_for_download, read_input_csv, write_output_csv,test_dataset_availability_and_save_it
from test_availability_data.utils.download import Downloader

class FakeDownloader:
    def run(self, attempts):
        return {
            "downloadable": True,
            "last_downloadable_time": "2023-01-01 01:00:00",
            "commands": ["cmd1", "cmd2", "cmd3"],
            "errors": [None, None, None],
        }

def test_assign_regions(sample_df):
    def fake_region(dataset_id, region_identifier):
        return "region_x"
    
    df = assign_regions(sample_df.copy(), region_identifier="ignored")
    assert "region" in df.columns
    assert all(df["region"] == "region_x")

def test_process_row_with_downloader(monkeypatch, sample_df):
    row = sample_df.iloc[0]

    # Patch Downloader to use FakeDownloader
    monkeypatch.setattr("test_availability_data.utils.download.Downloader", lambda data_dir: FakeDownloader())

    result = process_row_for_download(row, data_dir=".", region_identifier="dummy")
    assert result["downloadable"] is True
    assert result["first_command"] == "cmd1"
    assert result["first_error"] is None

def test_process_row_missing_time(sample_df):
    row = sample_df.iloc[1]  # last_available_time is None
    result = process_row_for_download(row, data_dir=".", region_identifier="dummy")
    assert result["downloadable"] is False
    assert result["first_error"] == "No last_available_time available"

def test_full_downloading_datasets(monkeypatch, sample_df, tmp_path):
    # Fake CSV read
    monkeypatch.setattr("test_availability_data.downloading_datasets.read_input_csv", lambda _: sample_df.copy())

    # Fake write (capture output instead of writing to disk)
    writes = {}
    def fake_write(df, data_dir):
        writes["full"] = df
    monkeypatch.setattr("test_availability_data.downloading_datasets.write_output_csv", fake_write)

    # Fake Downloader
    class FakeDownloader:
        def run(self, attempts):
            return {
                "downloadable": True,
                "last_downloadable_time": "2023-01-01 01:00:00",
                "commands": ["cmd1", "cmd2", "cmd3"],
                "errors": [None, None, None],
            }
    monkeypatch.setattr("test_availability_data.utils.download.Downloader", lambda data_dir: FakeDownloader())

    df = test_dataset_availability_and_save_it(tmp_path, region_identifier="dummy")
    assert "downloadable" in df.columns
    assert writes["full"].equals(df)