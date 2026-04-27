from datetime import datetime

import pandas as pd
import uuid
import pytest
from sqlalchemy import select

from test_availability_data.database_management.schemas import (
    datasets_tested,
    errors,
    testing_metadata,
)


def _insert_test_run(db):
    return db.append_test_metadata(
        start_time=datetime(2024, 1, 1, 0, 0, 0),
        end_time=datetime(2024, 1, 1, 1, 0, 0),
        linux_version="5.15.0",
        toolbox_version="1.0.0",
        script_version="1.0.0",
        run_duration=3600,
        number_of_datasets=2,
    )


def test_append_test_metadata_returns_id(db):
    run_id = _insert_test_run(db)
    assert run_id is not None


def test_append_test_metadata_inserts_one_row(db):
    _insert_test_run(db)
    with db.engine.connect() as conn:
        rows = conn.execute(select(testing_metadata)).fetchall()
    assert len(rows) == 1


def test_append_dataset_downloadable_status(db, sample_csv):
    run_id = _insert_test_run(db)
    db.append_dataset_downloadable_status(sample_csv, run_id)

    with db.engine.connect() as conn:
        rows = conn.execute(select(datasets_tested)).fetchall()
    assert len(rows) == 2


def test_append_errors_only_inserts_error_rows(db, sample_csv):
    run_id = _insert_test_run(db)
    db.append_dataset_downloadable_status(sample_csv, run_id)
    db.append_errors(sample_csv)

    with db.engine.connect() as conn:
        rows = conn.execute(select(errors)).fetchall()
    # second dataset row has two errors
    assert len(rows) == 2


def test_no_errors_when_all_downloadable(db, tmp_path):
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
            }
        ]
    )
    csv_path = tmp_path / "downloaded_datasets.csv"
    df.to_csv(csv_path, index=False)

    db.append_errors(tmp_path)

    with db.engine.connect() as conn:
        rows = conn.execute(select(errors)).fetchall()
    assert len(rows) == 0
