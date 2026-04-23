import argparse
import os


def get_duration_in_seconds_from_two_utc(start_time, end_time):
    duration = end_time - start_time

    duration_seconds = duration.total_seconds()

    return int(duration_seconds)


def get_configuration_from_command_line():
    parser = argparse.ArgumentParser(
        description="Analyze dataset downloadability and timing."
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        required=True,
        help="Path to the directory containing csv files",
    )
    parser.add_argument(
        "--max-products",
        type=int,
        default=None,
        help="Maximum number of products to test (default: all products)",
    )

    args = parser.parse_args()

    # Validate data directory
    if os.path.exists(args.data_dir) and not os.path.isdir(args.data_dir):
        raise NotADirectoryError(f"❌ '{args.data_dir}' exists but is not a directory.")

    # Create directory if needed
    os.makedirs(args.data_dir, exist_ok=True)

    return args.data_dir, args.max_products

def determine_region(dataset_id: str, region_dict: dict) -> str:
    for region, meta in region_dict.items():
        if any(keyword in dataset_id for keyword in meta["keywords"]):
            return region
    return "Global"
