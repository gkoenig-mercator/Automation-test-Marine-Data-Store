import pandas as pd
import copernicusmarine
import os
import re

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

def determine_region(dataset_id, region_identifier):
    for region in region_identifier:
        for keyword in region_identifier[region]['keywords']:
            if keyword in dataset_id:
               return region

    return 'Global'

region_identifier = {'Mediterranean': {'keywords': ['MEDSEA', 'MED_SST', 'MED_PHY', 'MED_BGC'],
                                       'min_lon':14,
                                       'max_lon': 15.5,
                                       'min_lat':42.5,
                                       'max_lat':44},
                     'Antarctic': {'keywords': ['ANT_PHY','antarctic'],
                                       'min_lon':-48,
                                       'max_lon': -40,
                                       'min_lat':-90,
                                       'max_lat':-60},
                     'Arctic': {'keywords': ['ARCTIC', 'ARC_BGC', 'SEA_ICE_GLO','SEAICE_ARC', 'INSITU_ARC'],
                                       'min_lon':-48,
                                       'max_lon': -40,
                                       'min_lat':-73,
                                       'max_lat':-68},
                     'Iberia-Biscay-Ireland': {'keywords': ['IBI'],
                                       'min_lon':-5.5,
                                       'max_lon': -3,
                                       'min_lat':44,
                                       'max_lat':47},
                     'NorthWestern European Shelf': {'keywords': ['NWSHELF', 'NWS', 'NORTHWESTSHELF'],
                                       'min_lon':2.5,
                                       'max_lon': 5,
                                       'min_lat':53,
                                       'max_lat':57},
                     'Atlantic North': {'keywords': ['ATL'],
                                       'min_lon':-16,
                                       'max_lon': -12,
                                       'min_lat':50,
                                       'max_lat':56},
                     'Baltic': {'keywords': ['BALTICSEA', 'BAL_BGC','SST_BAL', 'SEAICE_BAL','INSITU_BAL','BALTIC'],
                                       'min_lon':18,
                                       'max_lon': 20.5,
                                       'min_lat':61,
                                       'max_lat':62.5},
                    'Black Sea': {'keywords': ['BLKSEA', 'BLK_BGC','SST_BS','INSITU_BLK'],
                                       'min_lon':18,
                                       'max_lon': 20.5,
                                       'min_lat':61,
                                       'max_lat':62.5},
                    'Global': {'keywords': [],
                                       'min_lon':-38,
                                       'max_lon': -34,
                                       'min_lat':-3,
                                       'max_lat': 3}
                }

# Now we get the list of datasets
datasets_copernicus = copernicusmarine.describe()

dataset_informations = []

for product in datasets_copernicus.products:
    dataset_id = []
    for dataset in product.datasets:
        dataset_id = dataset.dataset_id
        version_label =[]
        region = determine_region(dataset_id, region_identifier)
        for version in dataset.versions:
            version_label = version.label
            part_name = []
            for part in version.parts[:1]:
                part_name = part.name
                service_name = []
                for service in part.services:
                    service_name = service.service_name
                    variable_name = []
                    for variable in service.variables[:1]:
                        variable_name = variable.standard_name
                        last_available_time = None
                        coordinate_name = []


                        if not variable.coordinates:
                            continue  # skip if no coordinates

                        for coordinate in variable.coordinates:
                            if 'time' in coordinate.coordinate_id:
                                coordinate_name = coordinate.coordinate_id
                                if coordinate.maximum_value:
                                    last_available_time = coordinate.maximum_value
                                else:
                                    last_available_time = coordinate.values[-1]
                                break  # Exit loop after finding the time coordinate

                     # Here we must determine the region to constrain the retrieval
                    dataset_informations.append({'dataset_id': dataset_id,
                                                 'region': region,
                                                 'dataset_version': version_label,
                                                 'version_part': part_name,
                                                 'service_name': service_name,
                                                 'variable_name': variable_name,
                                                 'coordinate': coordinate_name,
                                                 'last_available_time': pd.Timestamp(last_available_time, unit='ms')})

# Now we prepare two lists

downloadable = []
last_downloadable_time = []

for info in dataset_informations:
    file_names = []
    if pd.isnull(info['last_available_time'])  == False:
        try:
            start_date = (info['last_available_time'] - pd.tseries.offsets.DateOffset(hours=1)).strftime('%Y-%m-%d %X')
            end_date = info['last_available_time'].strftime('%Y-%m-%d %X')
            file_name = copernicusmarine.subset(dataset_id = info['dataset_id'],start_datetime= start_date,
                                end_datetime = end_date,
                                maximum_depth = 1,
                                output_directory='data',
                                output_filename=f'test.nc',
                                minimum_longitude = region_identifier[info['region']]['min_lon'],
                                maximum_longitude = region_identifier[info['region']]['max_lon'],
                                minimum_latitude = region_identifier[info['region']]['min_lat'],
                                maximum_latitude = region_identifier[info['region']]['max_lat'])
            downloadable.append(True)
            last_downloadable_time.append(info['last_available_time'])
            os.remove('data/test.nc')
        except Exception as e:
            exception_message = str(e)
            try :
                start_date = (info['last_available_time'] - pd.tseries.offsets.DateOffset(hours=1)).strftime('%Y-%m-%d %X')
                end_date = info['last_available_time'].strftime('%Y-%m-%d %X')
                file_name = copernicusmarine.subset(dataset_id = info['dataset_id'],start_datetime= start_date,
                                end_datetime = end_date,
                                maximum_depth = 1,
                                output_directory='data',
                                output_filename=f'test.nc')
                downloadable.append(True)
                last_downloadable_time.append(info['last_available_time'])
                os.remove('data/test.nc')
            except Exception as e:
                exception_message = str(e)
                try:
                    start_date = (info['last_available_time'] - pd.tseries.offsets.DateOffset(hours=1)).strftime('%Y-%m-%d %X')
                    end_date = info['last_available_time'].strftime('%Y-%m-%d %X')
                    file_name = copernicusmarine.subset(dataset_id = info['dataset_id'],
                                output_directory='data',
                                output_filename=f'test.nc')
                    downloadable.append(True)
                    last_downloadable_time.append(info['last_available_time'])
                    os.remove('data/test.nc')

                except Exception as e:
                    downloadable.append(False)
                    last_downloadable_time.append(pd.NaT)

    else:
        downloadable.append(False)
        last_downloadable_time.append(pd.NaT)

df_informations_datasets = pd.DataFrame(dataset_informations)

df_informations_datasets['last_downloadable_time'] = last_downloadable_time
df_informations_datasets['downloadable'] = downloadable

df_informations_datasets.to_csv('downloaded_datasets.csv', index=True)

df_informations_reduced = df_informations_datasets[['dataset_id','dataset_version','version_part','downloadable']]

df_informations_reduced.to_csv('downloaded_datasets_reduced.csv', index=True)
