import os

import copernicusmarine
import pandas as pd

from test_availability_data.toolbox_wrapper.general import (
    check_if_there_is_time_coordinate,
    extract_last_available_time,
    filter_allowed_services,
    get_first_variable_with_a_time_coordinate,
)

ALLOWED_SERVICES = ["arco-geo-series", "arco-time-series"]
SKIPPED_PRODUCTS = {"INSITU_GLO_PHY_TS_DISCRETE_MY_013_001"}
DEFAULT_OUTPUT_FILENAME = "list_of_informations_from_the_describe.csv"
MAX_PARTS_PER_VERSION = 1


def collect_dataset_information(
    max_products: int | None = None,
    allowed_services: list[str] = ALLOWED_SERVICES,
    skipped_products: set[str] = SKIPPED_PRODUCTS,
    max_parts_per_version: int = MAX_PARTS_PER_VERSION,
) -> pd.DataFrame:
    datasets_copernicus = copernicusmarine.describe()
    dataset_informations = []

    for product in datasets_copernicus.products:
        if product.product_id in skipped_products:
            continue

        for dataset in product.datasets:
            for version in dataset.versions:
                for part in version.parts[:max_parts_per_version]:
                    for service in filter_allowed_services(
                        part.services, allowed_services
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
                            if idx is not None:
                                last_time = extract_last_available_time(
                                    service.variables[idx]
                                )
                            else:
                                continue

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

    return pd.DataFrame(
        dataset_informations[:max_products] if max_products else dataset_informations
    )


def collect_and_store_dataset_informations(
    data_dir: str,
    max_products: int | None = None,
    output_filename: str = DEFAULT_OUTPUT_FILENAME,
) -> None:
    df = collect_dataset_information(max_products)
    output_path = os.path.join(data_dir, output_filename)
    df.to_csv(output_path, index=False)
    print(f"Saved dataset into {output_path}")
