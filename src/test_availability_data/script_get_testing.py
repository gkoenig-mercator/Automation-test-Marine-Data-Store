import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tempfile import NamedTemporaryFile

import copernicusmarine
import pandas as pd

from test_availability_data.config import logger
from test_availability_data.environment_variables import (
    COPERNICUSMARINE_SERVICE_PASSWORD,
    COPERNICUSMARINE_SERVICE_USERNAME,
)

ALLOWED_SERVICES = {"original-files", "wmts"}
EXCLUDED_PRODUCTS = [
    "INSITU_GLO_PHY_TS_DISCRETE_MY_013_001",
    "INSITU_GLO_PHY_TS_OA_MY_013_052",
]
MAX_SIZE_MB = 2000


def _do_dry_run(base_info) -> tuple[dict, copernicusmarine.ResponseGet | None]:
    """Step 1: Basic dry run with just dataset_id."""
    try:
        result = copernicusmarine.get(
            dataset_id=base_info["dataset_id"],
            dry_run=True,
            disable_progress_bar=True,
            username=COPERNICUSMARINE_SERVICE_USERNAME,
            password=COPERNICUSMARINE_SERVICE_PASSWORD,
        )
        record = {
            **base_info,
            "status_message": f"{result.status} + {result.message}",
            "number_of_files": result.number_of_files_to_download,
            "total_size": result.total_size,
            "first_file": result.files[0].filename if result.files else "",
            "error": False,
            "error_message": "",
        }
        return record, result
    except Exception as e:
        record = {
            **base_info,
            "status_message": "Failed",
            "number_of_files": 0,
            "total_size": 0.0,
            "first_file": "",
            "error": True,
            "error_message": str(e),
        }
        return record, None


def _check_size_limit(
    base_info: dict,
    filename: str,
    file_list_path: str,
) -> tuple[copernicusmarine.ResponseGet | None, dict | None]:
    """
    Step 2: Check specific file size. Returns (result, error_record).
    """
    try:
        result = copernicusmarine.get(
            dataset_id=base_info["dataset_id"],
            dataset_version=base_info["dataset_version"],
            dataset_part=base_info["version_part"],
            file_list=file_list_path,
            dry_run=True,
            disable_progress_bar=True,
            username=COPERNICUSMARINE_SERVICE_USERNAME,
            password=COPERNICUSMARINE_SERVICE_PASSWORD,
        )

        if (result.total_size or 0) > MAX_SIZE_MB:
            error_message = f"File too big: {result.total_size}MB > {MAX_SIZE_MB}MB"
            error_record = {
                **base_info,
                "status_message": "Too big",
                "number_of_files": result.number_of_files_to_download,
                "total_size": result.total_size,
                "first_file": filename,
                "error": True,
                "error_message": error_message,
            }
            return None, error_record

        return result, None

    except Exception as e:
        error_record = {
            **base_info,
            "status_message": "Size check failed",
            "number_of_files": 0,
            "total_size": 0.0,
            "first_file": filename,
            "error": True,
            "error_message": str(e),
        }
        return None, error_record


def _do_download(base_info: dict, filename: str, file_list_path: str) -> dict:
    """Step 3: Download file and cleanup. Returns record for logging."""
    try:
        result = copernicusmarine.get(
            dataset_id=base_info["dataset_id"],
            dataset_version=base_info["dataset_version"],
            dataset_part=base_info["version_part"],
            file_list=file_list_path,
            output_directory="./",
            no_directories=True,
            disable_progress_bar=True,
            username=COPERNICUSMARINE_SERVICE_USERNAME,
            password=COPERNICUSMARINE_SERVICE_PASSWORD,
        )

        # Cleanup downloaded file
        try:
            filepath = os.path.join("./", filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass

        return {
            **base_info,
            "status_message": f"{result.status} + {result.message}",
            "number_of_files": result.number_of_files_to_download,
            "total_size": result.total_size,
            "first_file": result.files[0].filename if result.files else filename,
            "error": False,
            "error_message": "",
        }

    except Exception as e:
        return {
            **base_info,
            "status_message": "Download failed",
            "number_of_files": 0,
            "total_size": 0.0,
            "first_file": filename,
            "error": True,
            "error_message": str(e),
        }


def _process_service(base_info: dict) -> tuple[dict, dict | None]:
    """
    Process a single service: dry run, size check, and download.

    Using the file_list option to avoid relisting files for each step.
    """
    dry_record, dry_result = _do_dry_run(base_info)

    if not dry_result or not dry_result.files:
        return dry_record, None

    s3_filepath = dry_result.files[0].s3_url
    filename = dry_result.files[0].filename
    with NamedTemporaryFile(mode="w+", delete=True) as temp_file:
        temp_file.write(s3_filepath)
        temp_file.flush()

        # Size check
        _, error_record = _check_size_limit(
            base_info,
            filename,
            temp_file.name,
        )
        if error_record:
            return dry_record, error_record

        # Download
        dl_record = _do_download(
            base_info,
            filename,
            temp_file.name,
        )
        return dry_record, dl_record


def test_get_capabilities(data_dir, max_datasets: int | None = None):
    datasets_copernicus = copernicusmarine.describe(disable_progress_bar=True)
    dry_run_records = []
    download_records = []
    datasets_to_check = [
        dataset
        for product in datasets_copernicus.products
        for dataset in product.datasets
        if product.product_id not in EXCLUDED_PRODUCTS
    ]
    datasets_to_check = (
        datasets_to_check[:max_datasets] if max_datasets else datasets_to_check
    )

    # Collect all service tasks
    service_tasks = []
    for dataset in datasets_to_check:
        for version in dataset.versions:
            for part in version.parts[:1]:  # Only first part
                for service in [
                    s for s in part.services if s.service_name in ALLOWED_SERVICES
                ]:
                    base_info = {
                        "dataset_id": dataset.dataset_id,
                        "dataset_version": version.label,
                        "version_part": part.name,
                        "service_name": service.service_name,
                    }
                    service_tasks.append(base_info)

    # Process services in parallel
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(_process_service, base_info): base_info
            for base_info in service_tasks
        }
        for future in as_completed(futures):
            base_info = futures[future]
            logger.info(f"Processing: {base_info['dataset_id']}")
            dry_record, dl_record = future.result()
            dry_run_records.append(dry_record)
            if dl_record:
                download_records.append(dl_record)

    # Save results
    dry_run_path = os.path.join(data_dir, "get_products_dry_run.csv")
    products_downloaded_path = os.path.join(data_dir, "get_products_downloaded.csv")
    pd.DataFrame(dry_run_records).to_csv(dry_run_path, index=False)
    pd.DataFrame(download_records).to_csv(products_downloaded_path, index=False)
    logger.info(
        f"Done: {len(dry_run_records)} dry runs, "
        f"{len(download_records)} download attempts"
    )
