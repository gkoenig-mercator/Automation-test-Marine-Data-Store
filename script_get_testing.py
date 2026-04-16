import os
import copernicusmarine
import pandas as pd

ALLOWED_SERVICES = {'original-files', 'wmts'}
EXCLUDED_PRODUCTS = ["INSITU_GLO_PHY_TS_DISCRETE_MY_013_001", "INSITU_GLO_PHY_TS_OA_MY_013_052"]
MAX_SIZE_MB = 2000


def do_dry_run(base_info):
    """Step 1: Basic dry run with just dataset_id."""
    try:
        result = copernicusmarine.get(
            dataset_id=base_info["dataset_id"],
            dry_run=True,
            disable_progress_bar=True
        )
        record = {
            **base_info,
            "status_message": f"{result.status} + {result.message}",
            "number_of_files": result.number_of_files_to_download,
            "total_size": result.total_size,
            "first_file": result.files[0].filename if result.files else "",
            "error": False,
            "error_message": ""
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
            "error_message": str(e)
        }
        return record, None


def check_size_limit(base_info, filename, max_size_mb):
    """Step 2: Check specific file size. Returns (result, error_record)."""
    try:
        result = copernicusmarine.get(
            dataset_id=base_info["dataset_id"],
            dataset_version=base_info["dataset_version"],
            dataset_part=base_info["version_part"],
            filter=f"*{filename}*",
            dry_run=True,
            disable_progress_bar=True
        )
        
        if result.total_size > max_size_mb:
            error_record = {
                **base_info,
                "status_message": "Too big",
                "number_of_files": result.number_of_files_to_download,
                "total_size": result.total_size,
                "first_file": filename,
                "error": True,
                "error_message": f"File too big: {result.total_size}MB > {max_size_mb}MB"
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
            "error_message": str(e)
        }
        return None, error_record


def do_download(base_info, filename):
    """Step 3: Download file and cleanup. Returns record for logging."""
    try:
        result = copernicusmarine.get(
            dataset_id=base_info["dataset_id"],
            dataset_version=base_info["dataset_version"],
            dataset_part=base_info["version_part"],
            filter=f"*{filename}*",
            output_directory="./",
            no_directories=True,
            disable_progress_bar=True
        )
        
        # Cleanup downloaded file
        try:
            filepath = os.path.join("./", filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        except:
            pass
            
        return {
            **base_info,
            "status_message": f"{result.status} + {result.message}",
            "number_of_files": result.number_of_files_to_download,
            "total_size": result.total_size,
            "first_file": result.files[0].filename if result.files else filename,
            "error": False,
            "error_message": ""
        }
        
    except Exception as e:
        return {
            **base_info,
            "status_message": "Download failed",
            "number_of_files": 0,
            "total_size": 0.0,
            "first_file": filename,
            "error": True,
            "error_message": str(e)
        }


def test_get_capabilities(max_products: Optional[int] = None):
    datasets_copernicus = copernicusmarine.describe()
    dataset_informations_dry_run = []
    dataset_informations_download = []

    for product in datasets_copernicus.products[:max_products] if max_products else datasets_copernicus.products:
        if product.product_id in EXCLUDED_PRODUCTS:
            continue
            
        for dataset in product.datasets:
            for version in dataset.versions:
                for part in version.parts[:1]:  # Only first part
                    
                    # Filter services inline
                    for service in [s for s in part.services if s.service_name in ALLOWED_SERVICES]:
                        
                        print(f"Processing: {dataset.dataset_id}")
                        
                        # Common info used in all records
                        base_info = {
                            "dataset_id": dataset.dataset_id,
                            "dataset_version": version.label,
                            "version_part": part.name,
                            "service_name": service.service_name,
                        }
                        
                        # STEP 1: Dry run
                        dry_record, dry_result = do_dry_run(base_info)
                        dry_run_records.append(dry_record)
                        
                        if not dry_result or not dry_result.files:
                            continue
                            
                        filename = dry_result.files[0].filename
                        
                        # STEP 2: Size check
                        size_result, error_record = check_size_limit(base_info, filename, MAX_SIZE_MB)
                        if error_record:
                            download_records.append(error_record)
                            continue
                        
                        # STEP 3: Download
                        dl_record = do_download(base_info, filename)
                        download_records.append(dl_record)

    # Save results
    pd.DataFrame(dry_run_records).to_csv("get_products_dry_run.csv", index=False)
    pd.DataFrame(download_records).to_csv("get_products_downloaded.csv", index=False)
    print(f"Done: {len(dry_run_records)} dry runs, {len(download_records)} download attempts")


if __name__ == "__main__":
    test_get_capabilities()
