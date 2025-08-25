import pandas as pd
import copernicusmarine
import os
from test_availability_data.utils.general import (
    extract_last_available_time,
    filter_allowed_services,
    check_if_there_is_time_coordinate,
    get_first_variable_with_a_time_coordinate,
    get_data_directory_from_command_line,
)

ALLOWED_SERVICES = ["arco-geo-series", "arco-time-series"]


def collect_dataset_information() -> pd.DataFrame:

    datasets_copernicus = copernicusmarine.describe()
    dataset_informations = []

    for product in datasets_copernicus.products:
        for dataset in product.datasets:
            for version in dataset.versions:
                for part in version.parts[:1]:
                    for service in filter_allowed_services(
                        part.services, ALLOWED_SERVICES
                    ):
                        has_time = check_if_there_is_time_coordinate(service.variables)
                        variable_name = service.variables[0].standard_name
                        last_time = None
                        if has_time:
                            variable_name, idx = (
                                get_first_variable_with_a_time_coordinate(
                                    service.variables
                                )
                            )
                            last_time = extract_last_available_time(
                                service.variables[idx]
                            )

                        dataset_informations.append(
                            {
                                "dataset_id": dataset.dataset_id,
                                "dataset_version": version.label,
                                "version_part": part.name,
                                "service_name": service.service_name,
                                "variable_name": variable_name,
                                "has_time_coordinate": has_time,
                                "last_available_time": (
                                    pd.Timestamp(last_time, unit="ms")
                                    if last_time
                                    else None
                                ),
                            }
                        )

    return pd.DataFrame(dataset_informations)


def collect_and_store_dataset_informations(data_dir):
    df = collect_dataset_information()
    output_path = os.path.join(data_dir, "list_of_informations_from_the_describe.csv")
    df.to_csv(output_path, index=False)
    print(f"Saved dataset into {output_path}")


if __name__ == "__main__":
    data_dir = get_data_directory_from_command_line()
    collect_and_store_dataset_informations(data_dir)
