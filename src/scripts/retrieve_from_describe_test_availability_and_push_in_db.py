import os
from datetime import datetime

import copernicusmarine
from dotenv import load_dotenv

from scripts.script_get_testing import test_get_capabilities
from test_availability_data.config.region_config import region_identifier
from test_availability_data.database_management.Add_data_in_database import (
    append_dataset_downloadable_status_in_db,
    append_errors_in_db,
    append_test_metadata_in_db,
)
from test_availability_data.toolbox_wrapper.downloading_datasets import (
    check_dataset_availability_and_save_it,
)
from test_availability_data.toolbox_wrapper.extract_datasets_from_describe import (
    collect_and_store_dataset_informations,
)
from test_availability_data.results.analysis import (
    get_number_of_datasets_downloaded,
)
from test_availability_data.utils.miscellaneous import (
    get_configuration_from_command_line,
    get_duration_in_seconds_from_two_utc,
)
from test_availability_data.utils.obtaining_environment_versions import get_versions


def main():
    start_time = datetime.utcnow()
    load_dotenv()
    data_dir, max_products = get_configuration_from_command_line()
    copernicusmarine.login(
        username=os.environ["COPERNICUS_MARINE_USERNAME"],
        password=os.environ["COPERNICUS_SERVICE_PASSWORD"],
        force_overwrite=True,
    )
    versions = get_versions()
    collect_and_store_dataset_informations(data_dir, max_products)
    check_dataset_availability_and_save_it(data_dir, region_identifier)
    end_time = datetime.utcnow()
    run_duration = get_duration_in_seconds_from_two_utc(start_time, end_time)
    number_of_datasets = get_number_of_datasets_downloaded(data_dir)

    test_get_capabilities(data_dir, max_products)
    run_id = append_test_metadata_in_db(
        start_time,
        end_time,
        versions["linux_version"],
        versions["toolbox_version"],
        versions["script_version"],
        run_duration,
        number_of_datasets,
    )
    append_dataset_downloadable_status_in_db(data_dir, run_id)
    append_errors_in_db(data_dir)


#    create_markdown_file_from_csv(data_dir,versions['toolbox_version'],
#                                  number_of_datasets,
#                                  percentage_with_error)
#    deploy_on_gh_pages()
#    if not no_error_in_download(data_dir):
#        sending_mail()


if __name__ == "__main__":
    main()
