from src.test_availability_data.downloading_datasets import check_dataset_availability_and_save_it
from src.test_availability_data.extract_datasets_from_describe import collect_and_store_dataset_informations
from src.test_availability_data.Add_data_in_database import append_test_metadata_in_db, append_errors_in_db, append_dataset_downloadable_status_in_db
from src.test_availability_data.check_if_download_errors import no_error_in_download
from src.test_availability_data.utils.general import get_data_directory_from_command_line, get_duration_in_seconds_from_two_utc, get_number_of_datasets_downloaded
from src.test_availability_data.utils.region_config import region_identifier
from src.test_availability_data.obtaining_environment_versions import get_versions
from src.test_availability_data.script_to_markdown import create_markdown_file_from_csv, deploy_on_gh_pages

import copernicusmarine
import os
from dotenv import load_dotenv
from datetime import datetime


def main():
    start_time = datetime.utcnow()
    load_dotenv()
    
    data_dir = get_data_directory_from_command_line()
    copernicusmarine.login(
        username=os.environ["COPERNICUS_MARINE_USERNAME"],
        password=os.environ["COPERNICUS_SERVICE_PASSWORD"],
        force_overwrite=True,
    )
    collect_and_store_dataset_informations(data_dir)
    check_dataset_availability_and_save_it(data_dir, region_identifier)
    create_markdown_file_from_csv(data_dir)
    deploy_on_gh_pages()
    end_time = datetime.utcnow()
    run_duration = get_duration_in_seconds_from_two_utc(start_time, end_time)
    number_of_datasets = get_number_of_datasets_downloaded(data_dir)
    versions = get_versions()
    run_id = append_test_metadata_in_db(start_time, end_time, 
                               versions['linux_version'],
                               versions['toolbox_version'], 
                               versions['script_version'],
                               run_duration,
                                number_of_datasets
                                )
    append_dataset_downloadable_status_in_db(data_dir, run_id)
    append_errors_in_db(data_dir)
    print(no_error_in_download(data_dir))


if __name__ == "__main__":
    main()
