import os
from typing import Any

import copernicusmarine
import pandas as pd
from copernicusmarine import CopernicusMarineService, CopernicusMarineVariable

from test_availability_data.config import logger

ALLOWED_SERVICES = ["arco-geo-series", "arco-time-series"]
# TODO: check why it is skipped
SKIPPED_PRODUCTS = {"INSITU_GLO_PHY_TS_DISCRETE_MY_013_001"}
DEFAULT_OUTPUT_FILENAME = "list_of_informations_from_the_describe.csv"
MAX_PARTS_PER_VERSION = 1


def collect_dataset_information(
    max_products: int | None = None,
) -> pd.DataFrame:
    datasets_copernicus = copernicusmarine.describe(disable_progress_bar=True)
    dataset_informations = []

    for product in datasets_copernicus.products:
        if product.product_id in SKIPPED_PRODUCTS:
            continue

        for dataset in product.datasets:
            for version in dataset.versions:
                for part in version.parts[:MAX_PARTS_PER_VERSION]:
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
    logger.info(f"Saved dataset into {output_path}")


def extract_last_available_time(variable: CopernicusMarineVariable) -> Any:
    """Get the last available time from copernicusmarine variable metadata."""
    for coordinate in variable.coordinates:
        if coordinate.coordinate_id == "time":
            if coordinate.maximum_value:
                return coordinate.maximum_value
            if coordinate.values:
                return coordinate.values[-1]
    return None


def filter_allowed_services(
    services: list[CopernicusMarineService],
    allowed_services: list[str] | None = None,
) -> list[CopernicusMarineService]:
    """
    Return services that are in the allowed list, or all services if no filter is given.
    """
    if allowed_services is None:
        return services
    return [s for s in services if s.service_name in allowed_services]


def check_if_there_is_time_coordinate(
    variables: list[CopernicusMarineVariable],
) -> bool:
    """Check if any variable has a time coordinate."""
    return any(
        coord.coordinate_id == "time" for var in variables for coord in var.coordinates
    )


def get_first_variable_with_a_time_coordinate(
    variables: list[CopernicusMarineVariable],
) -> tuple[str | None, int | None]:
    """Get the name and index of the first variable that has a time coordinate."""
    for index, variable in enumerate(variables):
        for coordinate in variable.coordinates:
            if coordinate.coordinate_id == "time":
                return variable.short_name, index
    return None, None
