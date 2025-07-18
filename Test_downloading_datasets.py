import pandas as pd
import os
import argparse
import logging
from utils_download import determine_region, attempt_download
from region_config import region_identifier

logging.getLogger("copernicusmarine").setLevel("DEBUG")

def main(): 
    parser = argparse.ArgumentParser(description='Analyze dataset downloadability and timing.')
    parser.add_argument('--data-dir', type=str, required=True, help='Path to the directory containing downloaded_datasets.csv')
    args = parser.parse_args()

    csv_path = os.path.join(args.data_dir, 'list_of_informations_from_the_describe.csv')
    df = pd.read_csv(csv_path)

    regions = [determine_region(row.dataset_id, region_identifier) for _, row in df.iterrows()]
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
        result = attempt_download(info, region_identifier, args.data_dir)
        downloadable.append(result[0])
        last_downloadable_time.append(result[1])
        first_command.append(result[2])
        first_error.append(result[3])
        second_command.append(result[4])
        second_error.append(result[5])
        third_command.append(result[6])
        third_error.append(result[7])

    df["downloadable"] = downloadable
    df["last_downloadable_time"] = last_downloadable_time
    df["first_command"] = first_command
    df["first_error"] = first_error
    df["second_command"] = second_command
    df["second_error"] = second_error
    df["third_command"] = third_command
    df["third_error"] = third_error

    df.to_csv(os.path.join(args.data_dir, "downloaded_datasets.csv"), index=False)
    df[["dataset_id", "dataset_version", "version_part", "downloadable"]].to_csv(
        os.path.join(args.data_dir, "downloaded_datasets_reduced.csv"), index=False
    )

if __name__ == "__main__":
    main()