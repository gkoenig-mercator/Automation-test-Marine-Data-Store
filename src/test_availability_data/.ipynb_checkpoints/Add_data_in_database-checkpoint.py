import pandas as pd
from sqlalchemy import create_engine
import os
import uuid
from dotenv import load_dotenv
from test_availability_data.utils.general import get_data_directory_from_command_line

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


if __name__ == "__main__":

    data_dir = get_data_directory_from_command_line()
    append_data_in_db(data_dir)
