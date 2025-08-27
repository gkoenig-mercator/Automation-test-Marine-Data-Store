import pandas as pd
from sqlalchemy import create_engine, insert
import os
import uuid
from dotenv import load_dotenv
from src.test_availability_data.utils.general import get_data_directory_from_command_line
from src.test_availability_data.database_management.create_database_table import testing_metadata, errors

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


def append_data_in_db(data_dir):

    file_path = os.path.join(data_dir, "downloaded_datasets.csv")
    df = pd.read_csv(file_path)
    df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]

    df.to_sql(table_name, engine, if_exists="append", index=False, chunksize=500)

def append_test_metadata_in_db(start_time, end_time, linux_version, toolbox_version, script_version):

    with engine.begin() as conn:
        test_run = {
            "start_time": start_time,
            "end_time": end_time,
            "linux_version": linux_version,
            "toolbox_version": toolbox_version,
            "script_version": script_version,
        }
        result = conn.execute(insert(testing_metadata).values(test_run))
        test_id = result.inserted_primary_key[0]  # UUID of the new test run

# Recommended version for your use case - pandas-based bulk operations
def append_errors_in_db(data_dir):
    """
    Pandas-optimized version - perfect for teams comfortable with pandas
    and datasets up to a few thousand rows
    """
    file_path = os.path.join(data_dir, "downloaded_datasets.csv")
    df = pd.read_csv(file_path)
    
    df["dataset_test_id"] = [str(uuid.uuid4()) for _ in range(len(df))]
    
    # Reshape data to have one row per error using pandas operations
    error_rows = []
    
    for _, row in df.iterrows():
        dataset_id = row["dataset_test_id"]
        
        for error_col, cmd_col in zip(
            ["first_error", "second_error", "third_error"],
            ["first_command", "second_command", "third_command"]
        ):
            error_msg = row[error_col]
            if pd.notnull(error_msg) and error_msg != "None":
                error_rows.append({
                    "id": str(uuid.uuid4()),
                    "dataset_test_id": dataset_id,
                    "command": row[cmd_col],
                    "error_message": error_msg
                })
    
    if error_rows:
        # Convert to DataFrame and use pandas to_sql for bulk insert
        errors_df = pd.DataFrame(error_rows)
        
        # Use pandas to_sql - handles all SQL generation automatically
        errors_df.to_sql(
            name='errors',  # Replace with your actual table name
            con=engine,
            if_exists='append',
            index=False,
            method='multi'  # Optimized multi-row INSERTs
        )
        
        print(f"Successfully inserted {len(errors_df)} error records")
        return len(errors_df)
    else:
        print("No error records to insert")
        return 0

if __name__ == "__main__":

    data_dir = get_data_directory_from_command_line()
    append_data_in_db(data_dir)
