import pandas as pd
import os


def no_error_in_download(data_dir):
    csv_path = os.path.join(data_dir, "downloaded_datasets.csv")
    downloaded_datasets_df = pd.read_csv(csv_path)

    return (downloaded_datasets_df["downloadable"]).all()

def get_number_of_datasets_downloaded(data_dir, filename="downloaded_datasets.csv"):
    file_path = os.path.join(data_dir, filename)
    with open(file_path, "r", encoding="utf-8") as f:
        num_rows = sum(1 for _ in f) - 1

    return num_rows

