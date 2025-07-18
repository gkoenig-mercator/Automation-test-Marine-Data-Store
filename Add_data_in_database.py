import pandas as pd
import argparse
from sqlalchemy import create_engine
import os
from utils.general import get_data_directory_from_command_line

username = os.environ["DATABASE_USERNAME"]
password = os.environ["DATABASE_PASSWORD"]
database_url = os.environ.get("DATABASE_URL", "postgresql-238316.project-test-datasets-subsetting-toolbox")
database_name = os.environ.get("DATABASE_NAME","defaultdb")

table_name = "List_of_datasets"
engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{database_url}:5432/{database_name}')

def append_data_in_db(data_dir): 

    file_path = os.path.join(data_dir, "downloaded_datasets.csv")
    df = pd.read_csv(file_path)

    df.to_sql(table_name, engine, if_exists="append", index=False, chunksize=500)

if __name__ == "__main__":

    data_dir = get_data_directory_from_command_line()
    append_data_in_db(data_dir)