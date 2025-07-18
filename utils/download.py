import os
import pandas as pd
import copernicusmarine
from typing import Optional

def determine_region(dataset_id: str, region_dict: dict) -> str:
    for region, meta in region_dict.items():
        if any(keyword in dataset_id for keyword in meta["keywords"]):
            return region
    return "Global"

def remove_files(directory: str):
    for filename in os.listdir(directory):
        if filename.endswith(('.csv','.nc')):
            os.remove(os.path.join(directory,filename))

def build_subset_kwargs(info: dict, region: dict, data_dir: str,
                        variables: Optional[list[str]] = None,
                        maximum_depth: Optional[float] = 5):
    start_time = pd.Timestamp(info["last_available_time"]) - pd.Timedelta(hours=1)
    return {
        "dataset_id": info["dataset_id"],
        "start_datetime": start_time.strftime("%Y-%m-%d %X"),
        "end_datetime": info["last_available_time"],
        "output_directory": data_dir,
        "output_filename": "test.nc",
        "maximum_depth": maximum_depth,
        "minimum_longitude": region["min_lon"],
        "maximum_longitude": region["max_lon"],
        "minimum_latitude": region["min_lat"],
        "maximum_latitude": region["max_lat"],
        "service": info["service_name"],
        **({"variables": variables} if variables else {}),
    }

def attempt_download(info: dict, region_dict: dict,
                     data_dir: str):
    region_name = info["region"]
    region = region_dict[region_name]
    status = None

    # Initialize
    first_command = second_command = third_command = None
    first_error = second_error = third_error = None
    last_downloadable_time = pd.NaT
    downloadable = False

    # First attempt with a given variable
    try:
        kwargs = build_subset_kwargs(info, region, data_dir,
                                     [info["variable_name"]])
        first_command = f"copernicusmarine.subset({kwargs})"
        status = copernicusmarine.subset(**kwargs)
        downloadable = True
        remove_files(data_dir)
        last_downloadable_time = info["last_available_time"]
        return downloadable, last_downloadable_time, first_command, first_error, second_command, second_error, third_command, third_error
    except Exception as e1:
        first_error = str(e1)    
    # Second attempt with all variables
    try: 
        kwargs = build_subset_kwargs(info, region,
                                     data_dir)
        second_command = f"copernicusmarine.subset({kwargs})"
        status = copernicusmarine.subset(**kwargs)
        remove_files(data_dir)
        downloadable = True
        last_downloadable_time = info["last_available_time"]
        return downloadable, last_downloadable_time, first_command, first_error, second_command, second_error, third_command, third_error
    except Exception as e2:
        second_error = str(e2)

    # Attempt 3: no region info
    try:
        start_time = pd.Timestamp(info["last_available_time"]) - pd.Timedelta(hours=1)
        third_command = (
            f"copernicusmarine.subset(dataset_id={info['dataset_id']}, "
            f"start_datetime={start_time}, end_datetime={info['last_available_time']}, "
            f"variables={[info['variable_name']]}, output_directory={data_dir}, "
            f"output_filename='test.nc', service={info['service_name']})"
        )
        status = copernicusmarine.subset(
            dataset_id=info["dataset_id"],
            start_datetime=start_time.strftime("%Y-%m-%d %X"),
            end_datetime=info["last_available_time"],
            variables=[info["variable_name"]],
            output_directory=data_dir,
            output_filename="test.nc",
            service=info["service_name"],
        )
        remove_files(data_dir)
        downloadable = True
        last_downloadable_time = info["last_available_time"]
    except Exception as e3:
        third_error = str(e3)

    return downloadable, last_downloadable_time, first_command, first_error, second_command, second_error, third_command, third_error

        