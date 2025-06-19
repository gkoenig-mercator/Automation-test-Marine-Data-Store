import pandas as pd
import copernicusmarine
import os
import re
import argparse

# --- Argument parsing ---
parser = argparse.ArgumentParser(description='Analyze dataset downloadability and timing.')
parser.add_argument('--data-dir', type=str, required=True, help='Path to the directory containing downloaded_datasets.csv')
args = parser.parse_args()

# We need this function in case the datasets are not available at the good date
def extract_last_date(string_with_last_available_date):
    
    # Regular expression to extract the last date
    last_date_pattern = r"\[.*?, (\d{4}-\d{2}-\d{2})"

    # Find all matches and extract the last date
    matches = re.findall(last_date_pattern, string_with_last_available_date)
    if matches:
        last_date = matches[-1]  # Get the last match
        return last_date
    else:
        return None

def extract_last_available_time(variable):

    for coordinate in variable.coordinates:
        if  coordinate.coordinate_id == 'time':
            if coordinate.maximum_value:
                return coordinate.maximum_value
            else:
                return coordinate.values[-1]
        else:
            last_available_time = None

    return last_available_time

def filter_allowed_services(services, allowed_services=None):
    for service in services:
        if service.service_name not in allowed_services:
            continue
        else:
            yield service

def check_if_there_is_time_coordinate(variables):
    has_time_coordinate = False
    for variable in variables:
        for coordinate in variable.coordinates:
            if coordinate.coordinate_id == 'time':
                has_time_coordinate = True

    return has_time_coordinate

def get_first_variable_with_a_time_coordinate(variables):
    variable_with_time_coordinate = None
    index = 0
    for variable in variables:
        for coordinate in variable.coordinates:
            if coordinate.coordinate_id == 'time':
                variable_with_time_coordinate = variable.standard_name
                return variable_with_time_coordinate, index
        index+=1

    return None, None


allowed_services = ['omi-arco','arco-geo-series','arco-time-series']

# Now we get the list of datasets
datasets_copernicus = copernicusmarine.describe()

dataset_informations = []

for product in datasets_copernicus.products:
    dataset_id = None
    for dataset in product.datasets:
        dataset_id = dataset.dataset_id
        version_label =None
        for version in dataset.versions:
            version_label = version.label
            part_name = None
            for part in version.parts[:1]:
                part_name = part.name
                service_name = None
                for service in filter_allowed_services(part.services,allowed_services):
                    there_is_time_coordinate = False
                    last_available_time = None
                    service_name = service.service_name
                    variable_name = service.variables[0].standard_name
                    there_is_time_coordinate = check_if_there_is_time_coordinate(service.variables)
                    if there_is_time_coordinate:
                        variable_name, variable_index = get_first_variable_with_a_time_coordinate(service.variables)
                        last_available_time = extract_last_available_time(service.variables[variable_index]) 
                        
                    dataset_informations.append({'dataset_id': dataset_id,
                                                 'dataset_version': version_label,
                                                 'version_part': part_name,
                                                 'service_name': service_name,
                                                 'variable_name': variable_name,
                                                 'has_time_coordinate': there_is_time_coordinate,
                                                 'last_available_time': pd.Timestamp(last_available_time, unit='ms')})

df_informations_datasets = pd.DataFrame(dataset_informations)

df_informations_datasets.to_csv(os.path.join(args.data_dir, 'list_of_informations_from_the_describe.csv'),index=False)