import os
import uuid

import pandas as pd
from sqlalchemy import create_engine, insert

from test_availability_data.database_management.schemas import (
    datasets_tested,
    errors,
    testing_metadata,
)


class DatabaseManager:
    def __init__(self, database_url):
        self.engine = create_engine(database_url)

    def append_test_metadata(
        self,
        start_time,
        end_time,
        linux_version,
        toolbox_version,
        script_version,
        run_duration,
        number_of_datasets,
    ):
        test_run = {
            "start_time": start_time,
            "end_time": end_time,
            "run_duration_seconds": run_duration,
            "numbers_of_datasets": number_of_datasets,
            "linux_version": linux_version,
            "toolbox_version": toolbox_version,
            "script_version": script_version,
        }
        with self.engine.begin() as conn:
            result = conn.execute(insert(testing_metadata).values(test_run))
            if result.inserted_primary_key:
                return result.inserted_primary_key[0]
            raise Exception("Failed to retrieve test_id after inserting test metadata.")

    def append_dataset_downloadable_status(self, data_dir, test_id):
        file_path = os.path.join(data_dir, "downloaded_datasets.csv")
        df = pd.read_csv(file_path)

        dataset_rows = df.rename(columns={"first_command": "command"}).assign(
            id=df["id"].apply(lambda x: uuid.UUID(x) if pd.notna(x) else uuid.uuid4()),
            test_id=test_id,
            downloadable=df["downloadable"].map(
                lambda x: str(x).lower() == "true" if pd.notna(x) else False
            ),
            last_downloadable_time=df["last_downloadable_time"].where(
                pd.notna(df["last_downloadable_time"]), other=None
            ),
        )[
            [
                "id",
                "test_id",
                "dataset_id",
                "dataset_version",
                "version_part",
                "service_name",
                "variable_name",
                "command",
                "last_downloadable_time",
                "downloadable",
            ]
        ]

        if not dataset_rows.empty:
            with self.engine.begin() as conn:
                conn.execute(
                    insert(datasets_tested), dataset_rows.to_dict(orient="records")
                )

    def append_errors(self, data_dir):
        file_path = os.path.join(data_dir, "downloaded_datasets.csv")
        df = pd.read_csv(file_path)

        error_rows = []
        for _, row in df.iterrows():
            for error_col, cmd_col in zip(
                ["first_error", "second_error", "third_error"],
                ["first_command", "second_command", "third_command"],
            ):
                error_msg = row[error_col]
                if pd.notnull(error_msg) and error_msg != "None":
                    error_rows.append(
                        {
                            "id": uuid.uuid4(),
                            "dataset_test_id": uuid.UUID(row["id"]),
                            "command": row[cmd_col],
                            "error_message": error_msg,
                        }
                    )

        if error_rows:
            with self.engine.begin() as conn:
                conn.execute(insert(errors), error_rows)
