from datetime import datetime, timezone

import copernicusmarine

from test_availability_data.config.region_config import region_identifier
from test_availability_data.database_management.add_data import (
    append_dataset_downloadable_status_in_db,
    append_errors_in_db,
    append_test_metadata_in_db,
)
from test_availability_data.environment_variables import (
    COPERNICUSMARINE_PASSWORD,
    COPERNICUSMARINE_USERNAME,
)
from test_availability_data.results.analysis import (
    get_number_of_datasets_downloaded,
)
from test_availability_data.scripts.script_get_testing import test_get_capabilities
from test_availability_data.toolbox_wrapper.downloading_datasets import (
    DatasetAvailabilityChecker,
)
from test_availability_data.toolbox_wrapper.extract_datasets_from_describe import (
    collect_and_store_dataset_informations,
)
from test_availability_data.utils.io import write_availability_results
from test_availability_data.utils.miscellaneous import (
    get_configuration_from_command_line,
    get_duration_in_seconds_from_two_utc,
)
from test_availability_data.utils.obtaining_environment_versions import get_versions


def main():
    start_time = datetime.now(timezone.utc)
    data_dir, max_products = get_configuration_from_command_line()
    print(f"Data directory: {data_dir}, Max products: {max_products}")
    copernicusmarine.login(
        check_credentials_valid=True,
        username=COPERNICUSMARINE_USERNAME,
        password=COPERNICUSMARINE_PASSWORD,
    )
    print("Logged in to Copernicus Marine Service successfully.")
    versions = get_versions()
    print(f"Environment versions: {versions}")
    collect_and_store_dataset_informations(data_dir, max_products)
    print("Collected dataset information and stored it in CSV.")
    checker_dataset_availability_subset = DatasetAvailabilityChecker(
        data_dir=data_dir, region_dict=region_identifier
    )
    subset_availability_dataframe = checker_dataset_availability_subset.run()
    write_availability_results(subset_availability_dataframe, data_dir)
    end_time = datetime.now(timezone.utc)
    run_duration = get_duration_in_seconds_from_two_utc(start_time, end_time)
    number_of_datasets = get_number_of_datasets_downloaded(data_dir)
    print(f"Number of datasets downloaded: {number_of_datasets}")

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
    # TODO: make this file more central: the entrypoint to
    # run the whole process
    main()
