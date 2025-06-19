import pandas as pd
import copernicusmarine
import os

region_identifier = {'Mediterranean': {'keywords': ['MEDSEA', 'MED_SST', 'MED_PHY', 'MED_BGC', '_med_'],
                                       'min_lon':14,
                                       'max_lon': 15.5,
                                       'min_lat':42.5,
                                       'max_lat':44},
                     'Antarctic': {'keywords': ['ANT_PHY','antarctic','_ant_'],
                                       'min_lon':-48,
                                       'max_lon': -40,
                                       'min_lat':-90,
                                       'max_lat':-60},
                     'Arctic': {'keywords': ['ARCTIC', 'ARC_BGC', 'SEA_ICE_GLO','SEAICE_ARC', 'INSITU_ARC','_arc_','arctic'],
                                       'min_lon':-48,
                                       'max_lon': -40,
                                       'min_lat':68,
                                       'max_lat':73},
                     'Iberia-Biscay-Ireland': {'keywords': ['IBI','_ibi_'],
                                       'min_lon':-5.5,
                                       'max_lon': -3,
                                       'min_lat':44,
                                       'max_lat':47},
                     'NorthWestern European Shelf': {'keywords': ['NWSHELF', 'NWS', 'NORTHWESTSHELF','_nwshelf_'],
                                       'min_lon':2.5,
                                       'max_lon': 5,
                                       'min_lat':53,
                                       'max_lat':57},
                     'Atlantic North': {'keywords': ['ATL','_atl_'],
                                       'min_lon':-16,
                                       'max_lon': -12,
                                       'min_lat':50,
                                       'max_lat':56},
                     'Baltic': {'keywords': ['BALTICSEA', 'BAL_BGC','SST_BAL', 'SEAICE_BAL','INSITU_BAL','BALTIC','_bal_'],
                                       'min_lon':18,
                                       'max_lon': 20.5,
                                       'min_lat':61,
                                       'max_lat':62.5},
                    'Black Sea': {'keywords': ['BLKSEA', 'BLK_BGC','SST_BS','INSITU_BLK','_blk_'],
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

def determine_region(dataset_id, region_identifier):
    for region in region_identifier:
        for keyword in region_identifier[region]['keywords']:
            if keyword in dataset_id:
               return region
               
    return 'Global'

def download_in_given_region_and_time_period(info, region_identifier):
    start_date = (pd.Timestamp(info['last_available_time']) - pd.tseries.offsets.DateOffset(hours=1)).strftime('%Y-%m-%d %X')
    end_date = info['last_available_time']
    
    subset_status = copernicusmarine.subset(dataset_id = info['dataset_id'],
                                        start_datetime= start_date, 
                                        end_datetime = end_date,
                                        maximum_depth = 1,
                                        output_directory='data',
                                        output_filename=f'test.nc',
                                        minimum_longitude = region_identifier[info['region']]['min_lon'],
                                        maximum_longitude = region_identifier[info['region']]['max_lon'],
                                        minimum_latitude = region_identifier[info['region']]['min_lat'],
                                        maximum_latitude = region_identifier[info['region']]['max_lat'])

    return subset_status

def download_in_given_time_period(info):
    start_date = (pd.Timestamp(info['last_available_time']) - pd.tseries.offsets.DateOffset(hours=1)).strftime('%Y-%m-%d %X')
    end_date = info['last_available_time']
    
    subset_status = copernicusmarine.subset(dataset_id = info['dataset_id'],
                                        start_datetime= start_date, 
                                        end_datetime = end_date,
                                        output_directory='data',
                                        output_filename=f'test.nc')

    return subset_status

def download_whole_dataset(info):
    start_date = (pd.Timestamp(info['last_available_time']) - pd.tseries.offsets.DateOffset(hours=1)).strftime('%Y-%m-%d %X')
    end_date = info['last_available_time']
    subset_status = copernicusmarine.subset(dataset_id = info['dataset_id'],
                                        output_directory='data',
                                        output_filename=f'test.nc')

    return subset_status

downloadable = []
last_downloadable_time = []
regions = []

dataset_informations = pd.read_csv('list_of_informations_from_the_describe.csv')

copernicusmarine.login()

for index, dataset_information in dataset_informations.iterrows():
    regions.append(determine_region(dataset_information.dataset_id, region_identifier))

dataset_informations['region'] = regions

for index, dataset_information in dataset_informations.iterrows():
    subset_status = None
    if pd.isnull(dataset_information['last_available_time'])  == False:
        print(dataset_information.region, dataset_information.dataset_id)
        try:
            subset_status = download_in_given_region_and_time_period(dataset_information, region_identifier)
            print(subset_status.message, subset_status.status)
            downloadable.append(True)
            last_downloadable_time.append(dataset_information['last_available_time'])
            os.remove('data/test.nc')
        except Exception as e:
            exception_message = str(e)
            print("There was an error", exception_message)
            try :
                subset_status = download_in_given_time_period(dataset_information)
                print(subset_status.message, subset_status.status)
                downloadable.append(True)
                last_downloadable_time.append(dataset_information['last_available_time'])
                os.remove('data/test.nc')
            except Exception as e:
                exception_message = str(e)
                print("There was a second error", exception_message)
                try: 
                    subset_status = download_whole_dataset(dataset_information)
                    print(subset_status.message, subset_status.status)
                    downloadable.append(True)
                    last_downloadable_time.append(dataset_information['last_available_time'])
                    os.remove('data/test.nc')

                except Exception as e:
                    print("There was a third error", exception_message)
                    downloadable.append(False)
                    last_downloadable_time.append(pd.NaT)
                    
    else:
        downloadable.append(False)
        last_downloadable_time.append(pd.NaT)

dataset_informations['last_downloadable_time'] = last_downloadable_time
dataset_informations['downloadable'] = downloadable

dataset_informations.to_csv('downloaded_datasets.csv', index=True)

dataset_informations_reduced = dataset_informations[['dataset_id','dataset_version','version_part','downloadable']]

dataset_informations_reduced.to_csv('downloaded_datasets_reduced.csv', index=True)