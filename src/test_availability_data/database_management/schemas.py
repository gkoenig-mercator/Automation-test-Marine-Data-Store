import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
)

metadata = MetaData(schema="testing")

# --- 1. Testing metadata ---
testing_metadata = Table(
    "test_runs",
    metadata,
    Column("id", String, primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("start_time", DateTime, default=datetime.utcnow),
    Column("end_time", DateTime),
    Column("run_duration_seconds", Integer),
    Column("numbers_of_datasets", Integer),
    Column("linux_version", String),
    Column("toolbox_version", String),
    Column("script_version", String),
)

# --- 2. Datasets tested ---
datasets_tested = Table(
    "test_run_datasets",
    metadata,
    Column("id", String, primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("test_id", String, ForeignKey("test_runs.id")),
    Column("dataset_id", String),
    Column("dataset_version", String),
    Column("version_part", String),
    Column("service_name", String),
    Column("variable_name", String),
    Column("command", Text),
    Column("last_downloadable_time", String),
    Column("downloadable", Boolean),
)

# --- 3. Errors ---
errors = Table(
    "test_run_dataset_errors",
    metadata,
    Column("id", String, primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("dataset_test_id", String, ForeignKey("test_run_datasets.id")),
    Column("command", Text),
    Column("error_message", Text),
)
