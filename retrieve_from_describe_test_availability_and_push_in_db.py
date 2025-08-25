from src.test_availability_data.downloading_datasets import check_dataset_availability_and_save_it
from src.test_availability_data.extract_datasets_from_describe import collect_and_store_dataset_informations
from src.test_availability_data.Add_data_in_database import append_data_in_db
from src.test_availability_data.check_if_download_errors import no_error_in_download
from src.test_availability_data.utils.general import get_data_directory_from_command_line
from src.test_availability_data.utils.region_config import region_identifier

import copernicusmarine
import os
from dotenv import load_dotenv


def main():
    load_dotenv()
    data_dir = get_data_directory_from_command_line()
    copernicusmarine.login(
        username=os.environ["COPERNICUS_MARINE_USERNAME"],
        password=os.environ["COPERNICUS_SERVICE_PASSWORD"],
        force_overwrite=True,
    )
    collect_and_store_dataset_informations(data_dir)
    check_dataset_availability_and_save_it(data_dir, region_identifier)
    append_data_in_db(data_dir)
    print(no_error_in_download(data_dir))


if __name__ == "__main__":
    main()
