import pandas as pd
import os
from src.test_availability_data.utils.general import get_data_directory_from_command_line


def no_error_in_download(data_dir):
    csv_path = os.path.join(data_dir, "downloaded_datasets.csv")
    downloaded_datasets_df = pd.read_csv(csv_path)

    return (downloaded_datasets_df["downloadable"]).all()


if __name__ == "__main__":
    data_dir = get_data_directory_from_command_line()
    print(no_error_in_download(data_dir))
