import logging
import os
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

from test_availability_data.utils.miscellaneous import determine_region


from test_availability_data.toolbox_wrapper.download import Downloader

logging.getLogger("copernicusmarine").setLevel("DEBUG")


def read_input_csv(data_dir, filename="list_of_informations_from_the_describe.csv"):
    path = os.path.join(data_dir, filename)
    return pd.read_csv(path)


def write_output_csv(
    df,
    data_dir,
    full_filename="downloaded_datasets.csv",
    reduced_filename="downloaded_datasets_reduced.csv",
    error_filename="datasets_not_downloaded.csv",
):
    df.to_csv(os.path.join(data_dir, full_filename), index=False)
    df[["dataset_id", "dataset_version", "version_part", "downloadable"]].to_csv(
        os.path.join(data_dir, reduced_filename), index=False
    )
    df_with_error = df.copy()
    df_with_error = df_with_error[~df_with_error["downloadable"]]
    df_with_error.to_csv(os.path.join(data_dir, error_filename), index=False)


def assign_regions(df, region_dict):
    df["region"] = df["dataset_id"].apply(lambda ds: determine_region(ds, region_dict))
    return df


def process_row_for_download(row, data_dir, region_dict, downloader_cls=Downloader):
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
    downloader = downloader_cls(info, region_dict, data_dir)
    result = downloader.run()

    return {
        "downloadable": result["downloadable"],
        "last_downloadable_time": result["last_downloadable_time"],
        "first_command": result["commands"][0],
        "first_error": result["errors"][0],
        "second_command": result["commands"][1] if len(result["commands"]) > 1 else None,
        "second_error": result["errors"][1] if len(result["errors"]) > 1 else None,
        "third_command": result["commands"][2] if len(result["commands"]) > 2 else None,
        "third_error": result["errors"][2] if len(result["errors"]) > 2 else None,
    }


def process_dataframe(df, data_dir, region_dict):
    results = df.apply(
        lambda row: process_row_for_download(row, data_dir, region_dict),
        axis=1,
        result_type="expand",
    )
    df = pd.concat([df, results], axis=1)
    return df


def process_dataframe_parallel(df, data_dir, region_dict, max_workers=4):
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_row_for_download, row, data_dir, region_dict): idx
            for idx, row in df.iterrows()
        }

        for future in as_completed(futures):
            idx = futures[future]
            try:
                results.append((idx, future.result()))
            except Exception as e:
                results.append((idx, {"downloadable": False, "error": str(e)}))

    results_sorted = [res for _, res in sorted(results, key=lambda x: x[0])]
    results_df = pd.DataFrame(results_sorted, index=df.index)

    return pd.concat([df, results_df], axis=1)


def check_dataset_availability_and_save_it(
    data_dir, region_dict, parallel=False, max_workers=4
):
    df = read_input_csv(data_dir)
    df = assign_regions(df, region_dict)

    if parallel:
        df = process_dataframe_parallel(df, data_dir, region_dict, max_workers=max_workers)
    else:
        df = process_dataframe(df, data_dir, region_dict)

    df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]

    write_output_csv(df, data_dir)
    return df
