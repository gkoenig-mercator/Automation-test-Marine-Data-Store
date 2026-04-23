import os

import pandas as pd


def write_availability_results(
    df: pd.DataFrame,
    data_dir: str,
    full_filename: str = "downloaded_datasets.csv",
    reduced_filename: str = "downloaded_datasets_reduced.csv",
    error_filename: str = "datasets_not_downloaded.csv",
):
    df.to_csv(os.path.join(data_dir, full_filename), index=False)

    df[["dataset_id", "dataset_version", "version_part", "downloadable"]].to_csv(
        os.path.join(data_dir, reduced_filename), index=False
    )

    df[~df["downloadable"]].to_csv(os.path.join(data_dir, error_filename), index=False)
