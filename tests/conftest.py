# tests/conftest.py
import pandas as pd
import pytest

@pytest.fixture
def sample_df():
    return pd.DataFrame([
        {"dataset_id": "ds1", "dataset_version": "v1", "version_part": 1, "last_available_time": "2023-01-01 00:00:00"},
        {"dataset_id": "ds2", "dataset_version": "v1", "version_part": 2, "last_available_time": None},
    ])