import pandas as pd
import os


def no_error_in_download(data_dir):
    csv_path = os.path.join(data_dir, "downloaded_datasets.csv")
    downloaded_datasets_df = pd.read_csv(csv_path)

    return (downloaded_datasets_df["downloadable"]).all()
