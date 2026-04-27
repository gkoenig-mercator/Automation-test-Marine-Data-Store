from datetime import timezone, datetime
import os
import uuid

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
    UUID,
)

SCHEMA = os.getenv("DB_SCHEMA", "testing")
schema_prefix = f"{SCHEMA}." if SCHEMA else ""
metadata = MetaData(schema=SCHEMA or None)

# --- 1. Testing metadata ---
testing_metadata = Table(
    "test_runs",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("start_time", DateTime, default=lambda: datetime.now(timezone.utc)),
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
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("test_id", UUID(as_uuid=True), ForeignKey(f"{schema_prefix}test_runs.id")),
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
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column(
        "dataset_test_id",
        UUID(as_uuid=True),
        ForeignKey(f"{schema_prefix}test_run_datasets.id"),
    ),
    Column("command", Text),
    Column("error_message", Text),
)
