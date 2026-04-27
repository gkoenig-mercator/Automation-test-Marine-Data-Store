import os

os.environ["DB_SCHEMA"] = ""  # must be before any local imports

import uuid
from datetime import datetime

import pandas as pd
import pytest
from sqlalchemy import create_engine, event

from test_availability_data.database_management.add_data import DatabaseManager
from test_availability_data.database_management.schemas import metadata


@pytest.fixture
def db():
    manager = DatabaseManager("sqlite:///:memory:")

    @event.listens_for(manager.engine, "connect")
    def disable_fks(connection, _):
        connection.execute("PRAGMA foreign_keys=OFF")

    metadata.create_all(manager.engine)
    return manager


@pytest.fixture
def sample_csv(tmp_path):
    df = pd.DataFrame(
        [
            {
                "id": str(uuid.uuid4()),
                "dataset_id": "cmems_mod_glo_phy",
                "dataset_version": "202406",
                "version_part": "default",
                "service_name": "arco-geo-series",
                "variable_name": "thetao",
                "first_command": "copernicusmarine get ...",
                "second_command": None,
                "third_command": None,
                "last_downloadable_time": "2024-01-01T00:00:00",
                "downloadable": True,
                "first_error": None,
                "second_error": None,
                "third_error": None,
            },
            {
                "id": str(uuid.uuid4()),
                "dataset_id": "cmems_mod_glo_phy",
                "dataset_version": "202406",
                "version_part": "default",
                "service_name": "arco-geo-series",
                "variable_name": "so",
                "first_command": "copernicusmarine get ...",
                "second_command": "copernicusmarine subset ...",
                "third_command": None,
                "last_downloadable_time": None,
                "downloadable": False,
                "first_error": "TimeoutError: connection timed out",
                "second_error": "ConnectionError: failed",
                "third_error": None,
            },
        ]
    )
    csv_path = tmp_path / "downloaded_datasets.csv"
    df.to_csv(csv_path, index=False)
    return tmp_path
