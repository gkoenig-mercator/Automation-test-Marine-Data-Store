import pandas as pd
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from test_availability_data.utils.download import determine_region, Downloader, build_attempts
from test_availability_data.utils.region_config import region_identifier
from test_availability_data.utils.general import get_data_directory_from_command_line

logging.getLogger("copernicusmarine").setLevel("DEBUG")


def read_input_csv(data_dir, filename="list_of_informations_from_the_describe.csv"):
    path = os.path.join(data_dir, filename)
    return pd.read_csv(path)

def write_output_csv(df, data_dir, full_filename="downloaded_datasets.csv", reduced_filename="downloaded_datasets_reduced.csv"):
    df.to_csv(os.path.join(data_dir, full_filename), index=False)
    df[["dataset_id", "dataset_version", "version_part", "downloadable"]].to_csv(
        os.path.join(data_dir, reduced_filename), index=False
    )

def assign_regions(df, region_identifier):
    df["region"] = df["dataset_id"].apply(lambda ds: determine_region(ds, region_identifier))
    return df

def process_row_for_download(row, data_dir, region_identifier):
    if pd.isnull(row["last_available_time"]):
        return {
            "downloadable": False,
            "last_downloadable_time": pd.NaT,
            "first_command": None,
            "first_error": "No last_available_time available",
            "second_command": None,
            "second_error": None,
            "third_command": None,
            "third_error": None,
        }

    info = row.to_dict()
    downloader = Downloader(data_dir)
    attempts = build_attempts(info, region_identifier, data_dir)
    result = downloader.run(attempts)

    return {
        "downloadable": result["downloadable"],
        "last_downloadable_time": result["last_downloadable_time"],
        "first_command": result["commands"][0],
        "first_error": result["errors"][0],
        "second_command": result["commands"][1],
        "second_error": result["errors"][1],
        "third_command": result["commands"][2],
        "third_error": result["errors"][2],
    }

def process_dataframe(df, data_dir, region_identifier):
    results = df.apply(
        lambda row: process_row_for_download(row, data_dir, region_identifier),
        axis=1, result_type='expand'
    )
    df = pd.concat([df, results], axis=1)
    return df

def process_dataframe_parallel(df, data_dir, region_identifier, max_workers=4):
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # submit all tasks
        futures = {
            executor.submit(process_row_for_download, row, data_dir, region_identifier): idx
            for idx, row in df.iterrows()
        }

        # collect results as they finish
        for future in as_completed(futures):
            idx = futures[future]
            try:
                results.append((idx, future.result()))
            except Exception as e:
                # in case something goes really wrong
                results.append((idx, {"downloadable": False, "error": str(e)}))

    # Rebuild into a DataFrame in the correct order
    results_sorted = [res for _, res in sorted(results, key=lambda x: x[0])]
    results_df = pd.DataFrame(results_sorted, index=df.index)
    
    return pd.concat([df, results_df], axis=1)

def test_dataset_availability_and_save_it(data_dir, region_identifier, parallel=False, max_workers=4):
    df = read_input_csv(data_dir)
    df = assign_regions(df, region_identifier)
    
    if parallel:
        df = process_dataframe_parallel(df, data_dir, region_identifier, max_workers=max_workers)
    else:
        df = process_dataframe(df, data_dir, region_identifier)

    write_output_csv(df, data_dir)
    return df


if __name__ == "__main__":

    data_dir = get_data_directory_from_command_line()
    test_dataset_availability_and_save_it(data_dir, region_identifier, parallel=True)
