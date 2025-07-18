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

    results = {
        "downloadable": [],
        "last_downloadable_time":[],
        "errors": [],
        "commands":[],
    }

    for _, row in df.iterrows():
        if pd.isnull(row['last_available_time']):
            results["downloadable"].append(False)
            results["last_downloadable_time"].append(pd.NaT)
            results["errors"].append("No last_available_time available")
            results["commands"].append(None)

        info = row.to_dict()
        success, last_time, error, command = attempt_download(info, region_identifier)
        results["downloadable"].append(success)
        results["last_downloadable_time"].append(last_time)
        results["errors"].append(error)
        results["commands"].append(command)

    df["downloadable"] = results["downloadable"]
    df["last_downloadable_time"] = results["last_downloadable_time"]
    df["download_errors"] = results["errors"]
    df["download_commands"] = results["commands"]

    final_file_path = os.path.join(args.data_dir, "downloaded_datasets.csv")
    df.to_csv(final_file_path, index= False)
        
    df[["dataset_id", "dataset_version", "version_part", "downloadable"]].to_csv(
        os.path.join(args.data_dir, "downloaded_datasets_reduced.csv"), index=False
    )

if __name__ == "__main__":
    main()