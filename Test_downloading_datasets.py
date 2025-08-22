import pandas as pd
import os
import logging
from utils.download import determine_region, Downloader
from utils.region_config import region_identifier
from utils.general import get_data_directory_from_command_line

logging.getLogger("copernicusmarine").setLevel("DEBUG")


def test_dataset_availability_and_save_it(data_dir):
    csv_path = os.path.join(data_dir, "list_of_informations_from_the_describe.csv")
    df = pd.read_csv(csv_path)

    regions = [
        determine_region(row.dataset_id, region_identifier) for _, row in df.iterrows()
    ]
    df["region"] = regions

    # Prepare lists for results
    downloadable = []
    last_downloadable_time = []
    first_command = []
    second_command = []
    third_command = []
    first_error = []
    second_error = []
    third_error = []

    for _, row in df.iterrows():
        if pd.isnull(row["last_available_time"]):
            downloadable.append(False)
            last_downloadable_time.append(pd.NaT)
            first_command.append(None)
            second_command.append(None)
            third_command.append(None)
            first_error.append("No last_available_time available")
            second_error.append(None)
            third_error.append(None)
            continue

        info = row.to_dict()
        downloader = Downloader(info, region_identifier, data_dir)
        result = downloader.run()
        downloadable.append(result['downloadable'])
        last_downloadable_time.append(result['last_downloadable_time'])
        first_command.append(result['commands'][0])
        first_error.append(result['errors'][0])
        second_command.append(result['commands'][1])
        second_error.append(result['errors'][1])
        third_command.append(result['commands'][2])
        third_error.append(result['errors'][2])

    df["downloadable"] = downloadable
    df["last_downloadable_time"] = last_downloadable_time
    df["first_command"] = first_command
    df["first_error"] = first_error
    df["second_command"] = second_command
    df["second_error"] = second_error
    df["third_command"] = third_command
    df["third_error"] = third_error

    df.to_csv(os.path.join(data_dir, "downloaded_datasets.csv"), index=False)
    df[["dataset_id", "dataset_version", "version_part", "downloadable"]].to_csv(
        os.path.join(data_dir, "downloaded_datasets_reduced.csv"), index=False
    )


if __name__ == "__main__":

    data_dir = get_data_directory_from_command_line()
    test_dataset_availability_and_save_it(data_dir)
