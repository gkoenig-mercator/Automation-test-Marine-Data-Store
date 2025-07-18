from sqlalchemy import insert, Table, Column, Integer, String, MetaData, Float, inspect, create_engine
import uuid
import os
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

username = os.environ["DATABASE_USERNAME"]
password = os.environ["DATABASE_PASSWORD"]
database_url = os.environ.get("DATABASE_URL", "postgresql-238316.project-test-datasets-subsetting-toolbox")
database_name = os.environ.get("DATABASE_NAME","defaultdb")

name = "List_of_datasets"
engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{database_url}:5432/{database_name}')

def create_table(engine, name):
    metadata = MetaData()
    table = Table(
    name, metadata,
    Column('id', String, primary_key=True,
           default=lambda: str(uuid.uuid4())),
    Column('dataset_id',String),
    Column('dataset_version', String),
    Column('version_part', String),
    Column('service_name', String),
    Column('variable_name', String),
    Column('has_time_coordinate', String),
    Column('last_available_time',String),
    Column('region', String),
    Column('downloadable', String),
    Column('last_downloadable_time', String),
    Column('first_command', String),
    Column('first_error', String),
    Column('second_command', String),
    Column('second_error', String),
    Column('third_command', String),
    Column('third_error', String),
    schema="public"
    )

    metadata.create_all(engine)
    
    return table

def main():
    create_table(engine, name)

if __name__ == "__main__":
    main()