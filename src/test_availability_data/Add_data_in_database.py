import pandas as pd
from sqlalchemy import create_engine, insert
import os
import csv
import uuid
from dotenv import load_dotenv
from src.test_availability_data.utils.general import get_data_directory_from_command_line
from src.test_availability_data.database_management.create_database_table import testing_metadata, errors, datasets_tested

load_dotenv()

api_key = os.getenv("API_KEY")
username = os.environ["DATABASE_USERNAME"]
password = os.environ["DATABASE_PASSWORD"]
database_url = os.environ["DATABASE_URL"]
database_name = os.environ["DATABASE_NAME"]
database_port = os.environ["DATABASE_PORT"]

table_name = "List_of_datasets"
engine = create_engine(
    f"postgresql+psycopg2://{username}:{password}@{database_url}:{database_port}/{database_name}"
)

def append_test_metadata_in_db(start_time, end_time, linux_version, toolbox_version,
                               script_version, run_duration, number_of_datasets):

    with engine.begin() as conn:
        test_run = {
            "start_time": start_time,
            "end_time": end_time,
            "run_duration_seconds": run_duration,
            "numbers_of_datasets": number_of_datasets,
            "linux_version": linux_version,
            "toolbox_version": toolbox_version,
            "script_version": script_version,
        }
        result = conn.execute(insert(testing_metadata).values(test_run))
        test_id = result.inserted_primary_key[0]  # UUID of the new test run

    return test_id

# Recommended version for your use case - pandas-based bulk operations
def append_errors_in_db(data_dir):
    """
    Parse downloaded_datasets.csv, extract errors, and insert them into the DB.
    Each command with an error becomes one row in the `errors` table.
    """
    file_path = os.path.join(data_dir, "downloaded_datasets.csv")
    df = pd.read_csv(file_path)
    
    error_rows = []
    
    for _, row in df.iterrows():
        dataset_test_id = row["id"]  # <-- use CSV's "id" column
        
        for error_col, cmd_col in zip(
            ["first_error", "second_error", "third_error"],
            ["first_command", "second_command", "third_command"]
        ):
            error_msg = row[error_col]
            if pd.notnull(error_msg) and error_msg != "None":
                error_rows.append({
                    "id": str(uuid.uuid4()),             # unique ID for error row
                    "dataset_test_id": dataset_test_id,  # link back to test row
                    "command": row[cmd_col],
                    "error_message": error_msg
                })
    
    if error_rows:
        with engine.begin() as conn:
            conn.execute(insert(errors), error_rows)
        print(f"✅ Successfully inserted {len(errors)} error records")
        return len(errors_df)
    else:
        print("ℹ️ No error records to insert")
        return 0

def append_dataset_downloadable_status_in_db(data_dir, test_id):
    """
    Pandas-optimized version - perfect for teams comfortable with pandas
    and datasets up to a few thousand rows
    """
    
    file_path = os.path.join(data_dir, "downloaded_datasets.csv")
    dataset_rows = []

    # Read CSV and prepare rows
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dataset_rows.append({
                "id": row["id"],          # unique ID for this dataset_test row
                "test_id": test_id,               # link to the test_run
                "dataset_id": row["dataset_id"],
                "dataset_version": row["dataset_version"],
                "version_part": row["version_part"],
                "service_name": row["service_name"],
                "variable_name": row["variable_name"],
                "command": row["first_command"],  # rename column on the fly
                "last_downloadable_time": row["last_downloadable_time"],
                "downloadable": bool(row["downloadable"])
             })

    # Insert into database
    if dataset_rows:
        with engine.begin() as conn:
            conn.execute(insert(datasets_tested), dataset_rows)

if __name__ == "__main__":

    data_dir = get_data_directory_from_command_line()
    append_data_in_db(data_dir)
