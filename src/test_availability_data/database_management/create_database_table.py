from sqlalchemy import (
    Table, Column, String, Boolean, Integer, MetaData, DateTime, ForeignKey, Text, create_engine
)
import uuid
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

username = os.environ["DATABASE_USERNAME"]
password = os.environ["DATABASE_PASSWORD"]
database_url = os.environ.get(
    "DATABASE_URL", "postgresql-238316.project-test-datasets-subsetting-toolbox"
)
database_name = os.environ.get("DATABASE_NAME", "defaultdb")

engine = create_engine(
    f"postgresql+psycopg2://{username}:{password}@{database_url}:5432/{database_name}"
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
    Column("test_id", String, ForeignKey("testing.test_runs.id")),
    Column("dataset_id", String),
    Column("dataset_version", String),
    Column("version_part", String),
    Column("service_name", String),
    Column("variable_name", String),
    Column("command", Text),
    Column("last_downloadable_time", DateTime, default=datetime.utcnow),
    Column("downloadable", Boolean)
)

# --- 3. Errors ---
errors = Table(
    "test_run_dataset_errors",
    metadata,
    Column("id", String, primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("dataset_test_id", String, ForeignKey("testing.test_run_datasets.id")),
    Column("command", Text),
    Column("error_message", Text),
)

def create_schema(engine):
    engine.execute(text("CREATE SCHEMA IF NOT EXISTS testing"))
    metadata.create_all(engine)

if __name__ == "__main__":
    create_schema(engine)

