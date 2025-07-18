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

def build_subset_kwargs(info: dict, region: dict, variables: Optional[list[str]] = None,
                        maximum_depth: Optional[float] = 5):
    start_time = pd.Timestamp(info["last_available_time"]) - pd.Timedelta(hours=1)
    return {
        "dataset_id": info["dataset_id"],
        "start_datetime": start_time.strftime("%Y-%m-%d %X"),
        "end_datetime": info["last_available_time"],
        "output_directory": "data",
        "output_filename": "test.nc",
        "maximum_depth": maximum_depth,
        "minimum_longitude": region["min_lon"],
        "maximum_longitude": region["max_lon"],
        "minimum_latitude": region["min_lat"],
        "maximum_latitude": region["max_lat"],
        "service": info["service_name"],
        **({"variables": variables} if variables else {}),
    }

def attempt_download(info: dict, region_dict: dict):
    region_name = info["region"]
    region = region_dict[region_name]
    status = None

    # First attempt with a given variable
    try:
        print(f"Downloading for the first time")
        kwargs = build_subset_kwargs(info, region, [info["variable_name"]])
        status = copernicusmarine.subset(**kwargs)
        remove_files("data")
        return True, info["last_available_time"], None, f"copernicusmarine.subset({kwargs})"
    except Exception as e1:
        error1 = str(e1)
        print(str(e1))
    
    # Second attempt with all variables
    try: 
        print(f"Downloading for the second time")
        kwargs = build_subset_kwargs(info, region)
        status = copernicusmarine.subset(**kwargs)
        remove_files("data")
        return True, info["last_available_time"], None, f"copernicusmarine.subset({kwargs})"
    except Exception as e2:
        error2 = str(e2)

    # Attempt 3: no region info
    try:
        start_time = pd.Timestamp(info["last_available_time"]) - pd.Timedelta(hours=1)
        print(f"Downloading for the third time")
        status = copernicusmarine.subset(
            dataset_id=info["dataset_id"],
            start_datetime=start_time.strftime("%Y-%m-%d %X"),
            end_datetime=info["last_available_time"],
            variables=[info["variable_name"]],
            output_directory="data",
            output_filename="test.nc",
            service=info["service_name"],
        )
        remove_files("data")
        return True, info["last_available_time"], f"{error1}; {error2}", "copernicusmarine.subset(...) (no region)"
    except Exception as e3:
        return False, pd.NaT, f"{error1}; {error2}; {str(e3)}", None

        