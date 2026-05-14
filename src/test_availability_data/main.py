import argparse
import importlib.metadata
import os
import platform
from datetime import datetime, timezone
from time import time

import copernicusmarine
import distro
import pandas as pd

from test_availability_data.config import logger, region_identifier
from test_availability_data.database import (
    DatabaseManager,
)
from test_availability_data.email_sending import send_report_email
from test_availability_data.environment_variables import (
    COPERNICUSMARINE_SERVICE_PASSWORD,
    COPERNICUSMARINE_SERVICE_USERNAME,
    DATABASE_URL,
    MAXIMUM_DATASETS_TO_VALIDATE,
)
from test_availability_data.extract_datasets_from_describe import (
    collect_and_store_dataset_informations,
)
from test_availability_data.results_analysis import (
    get_number_of_datasets_downloaded,
)
from test_availability_data.script_get_testing import (
    test_get_capabilities,
)
from test_availability_data.toolbox_wrapper import (
    DatasetAvailabilityChecker,
)


def get_linux_version():
    try:
        return f"{distro.name()} {distro.version()} ({distro.codename()})"
    except Exception:
        return platform.platform()


def get_toolbox_version():
    try:
        return importlib.metadata.version("copernicusmarine")
    except importlib.metadata.PackageNotFoundError:
        return "not installed"


def get_script_version():
    try:
        return importlib.metadata.version("test_availability_data")
    except importlib.metadata.PackageNotFoundError:
        return "not installed"


def get_versions():
    return {
        "linux_version": get_linux_version(),
        "script_version": get_script_version(),
        "toolbox_version": get_toolbox_version(),
    }


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


if __name__ == "__main__":
    # Inputs
    parser = argparse.ArgumentParser(
        description="Analyze dataset downloadability and timing."
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        help="Path to the directory containing csv files",
        default="data",
    )
    parser.add_argument(
        "--max-datasets",
        type=int,
        default=None,
        help="Maximum number of datasets to test (default: all datasets)",
    )
    args = parser.parse_args()

    data_dir = args.data_dir
    if os.path.exists(args.data_dir) and not os.path.isdir(args.data_dir):
        raise NotADirectoryError(f"❌ '{args.data_dir}' exists but is not a directory.")
    os.makedirs(args.data_dir, exist_ok=True)

    max_datasets = args.max_datasets
    if not max_datasets and MAXIMUM_DATASETS_TO_VALIDATE:
        max_datasets = int(MAXIMUM_DATASETS_TO_VALIDATE)

    # Start of the process
    start_time = datetime.now(timezone.utc)
    logger.info(f"Starting dataset availability test, data directory: {data_dir}")
    if max_datasets:
        logger.info(f"Max datasets to test: {max_datasets}")
    db = DatabaseManager(DATABASE_URL)
    copernicusmarine.login(
        check_credentials_valid=True,
        username=COPERNICUSMARINE_SERVICE_USERNAME,
        password=COPERNICUSMARINE_SERVICE_PASSWORD,
    )
    logger.info("Logged in to Copernicus Marine Service successfully.")

    top_subset = time()
    logger.info("Collecting dataset information and storing it in CSV.")
    collect_and_store_dataset_informations(data_dir, max_datasets)
    logger.info("Collected dataset information and stored it in CSV.")

    logger.info("Checking dataset availability and storing results in CSV.")
    checker_dataset_availability_subset = DatasetAvailabilityChecker(
        data_dir=data_dir, region_dict=region_identifier
    )
    subset_availability_dataframe = checker_dataset_availability_subset.run()
    logger.info("Checked dataset availability and stored results in CSV.")

    write_availability_results(subset_availability_dataframe, data_dir)
    number_of_datasets = get_number_of_datasets_downloaded(data_dir)
    logger.info(
        f"Number of datasets downloaded: {number_of_datasets} in "
        f"{time() - top_subset} seconds for subset."
    )

    top_get = time()
    logger.info("Running get capabilities test.")
    test_get_capabilities(data_dir, max_datasets)
    logger.info(f"Finished in {time() - top_get} seconds for get.")

    logger.info("Storing dataset availability results in the database.")
    end_time = datetime.now(timezone.utc)
    versions = get_versions()
    run_id = db.append_test_metadata(
        start_time,
        end_time,
        versions["linux_version"],
        versions["toolbox_version"],
        versions["script_version"],
        (end_time - start_time).total_seconds(),
        number_of_datasets,
    )
    db.append_dataset_downloadable_status(data_dir, run_id)
    db.append_errors(data_dir)

    logger.info("Sending report email.")
    send_report_email(
        attachments=[
            os.path.join(data_dir, f)
            for f in [
                "datasets_not_downloaded.csv",
                "downloaded_datasets_reduced.csv",
                "downloaded_datasets.csv",
                "get_products_downloaded.csv",
                "get_products_dry_run.csv",
                "list_of_informations_from_the_describe.csv",
            ]
        ],
    )
