import copernicusmarine
from copernicusmarine import CopernicusMarineService
from typing import Optional, Generator
import os
import pandas as pd

ALLOWED_SERVICES = ['original-files','wmts']

def filter_allowed_services(
    services: list[CopernicusMarineService],
    allowed_services: Optional[list[str]] = None,
) -> Generator[CopernicusMarineService, None, None]:
    """Yield services in the authorized list"""
    for service in services:
        if service.service_name not in allowed_services:
            continue
        else:
            yield service

def get_filename(result_get):
    try:
        return result_get.files[0].filename
    except:
        return 'No file name found'

datasets_copernicus = copernicusmarine.describe()
dataset_informations_dry_run = []
dataset_informations_download = []

for product in datasets_copernicus.products[:86]:
    for dataset in product.datasets:
        for version in dataset.versions:
            for part in version.parts[:1]:
                for service in filter_allowed_services(
                    part.services, ALLOWED_SERVICES):
                    try:
                        result_dry_run = copernicusmarine.get(dataset_id=dataset.dataset_id, dry_run=True,
                                                             disable_progress_bar=True)
                        print(dataset.dataset_id)
                        dataset_informations_dry_run.append(
                            {"dataset_id": dataset.dataset_id,
                             "dataset_version": version.label,
                             "version_part": part.name,
                             "service_name": service.service_name,
                             "result_dry_run": f"{result_dry_run.status} + {result_dry_run.message}",
                             "number_of_files":result_dry_run.number_of_files_to_download,
                             "total_size_to_download":result_dry_run.total_size,
                             "first_file_to_download":get_filename(result_dry_run),
                             "error":False})
                    except Exception as e:
                        dataset_informations_dry_run.append(
                            {"dataset_id": dataset.dataset_id,
                             "dataset_version": version.label,
                             "version_part": part.name,
                             "service_name": service.service_name,
                             "result_dry_run": f"{result_dry_run.status} + {result_dry_run.message}",
                             "number_of_files":result_dry_run.number_of_files_to_download,
                             "total_size_to_download":result_dry_run.total_size,
                             "first_file_to_download":get_filename(result_dry_run),
                             "error":True})
                    try:
                        result_size_file = copernicusmarine.get(dataset_id= dataset.dataset_id,
                                                                dataset_version= version.label,
                                                                dataset_part= part.name,
                                                                filter=f"*{result_dry_run.files[0].filename}*",
                                                                dry_run=True)
                    except Exception as e:
                        dataset_informations_download.append(
                            {"dataset_id": dataset.dataset_id,
                             "dataset_version": version.label,
                             "version_part": part.name,
                             "service_name": service.service_name,
                             "result_dry_run": f"No file",
                             "number_of_files":0,
                             "total_size_to_download":0,
                             "first_file_to_download":"",
                             "error":True,
                             "error_message":"No file associated"})
                        continue
                        
                    if result_size_file.total_size > 2000: #Size is in Mb here
                        dataset_informations_download.append(
                            {"dataset_id": dataset.dataset_id,
                             "dataset_version": version.label,
                             "version_part": part.name,
                             "service_name": service.service_name,
                             "result_dry_run": f"{result_size_file.status} + {result_size_file.message}",
                             "number_of_files":result_size_file.number_of_files_to_download,
                             "total_size_to_download":result_size_file.total_size,
                             "first_file_to_download":get_filename(result_size_file),
                             "error":True,
                             "error_message":"File too big"})
                        continue
                        
                    try:
                        result = copernicusmarine.get(dataset_id= dataset.dataset_id, dataset_version= version.label,
                                                      dataset_part= part.name, output_directory='./',
                                                      filter=f"*{result_dry_run.files[0].filename}*",
                                                      no_directories=True)
                        dataset_informations_download.append(
                            {"dataset_id": dataset.dataset_id,
                             "dataset_version": version.label,
                             "version_part": part.name,
                             "service_name": service.service_name,
                             "result_dry_run": f"{result.status} + {result.message}",
                             "number_of_files":result.number_of_files_to_download,
                             "total_size_to_download":result.total_size,
                             "first_file_to_download":get_filename(result),
                             "error":False,
                             "error_message":""})
                        os.remove(result_dry_run.files[0].filename)
                    except Exception as e:
                        dataset_informations_download.append(
                            {"dataset_id": dataset.dataset_id,
                             "dataset_version": version.label,
                             "version_part": part.name,
                             "service_name": service.service_name,
                             "result_dry_run": f"{result.status} + {result.message}",
                             "number_of_files":result.number_of_files_to_download,
                             "total_size_to_download":result.total_size,
                             "first_file_to_download":'',
                             "error":True,
                             "error_message":e})

for product in datasets_copernicus.products[87:]:
    for dataset in product.datasets:
        for version in dataset.versions:
            for part in version.parts[:1]:
                for service in filter_allowed_services(
                    part.services, ALLOWED_SERVICES):
                    try:
                        result_dry_run = copernicusmarine.get(dataset_id=dataset.dataset_id, dry_run=True,
                                                             disable_progress_bar=True)
                        print(dataset.dataset_id)
                        dataset_informations_dry_run.append(
                            {"dataset_id": dataset.dataset_id,
                             "dataset_version": version.label,
                             "version_part": part.name,
                             "service_name": service.service_name,
                             "result_dry_run": f"{result_dry_run.status} + {result_dry_run.message}",
                             "number_of_files":result_dry_run.number_of_files_to_download,
                             "total_size_to_download":result_dry_run.total_size,
                             "first_file_to_download":get_filename(result_dry_run),
                             "error":False})
                    except Exception as e:
                        dataset_informations_dry_run.append(
                            {"dataset_id": dataset.dataset_id,
                             "dataset_version": version.label,
                             "version_part": part.name,
                             "service_name": service.service_name,
                             "result_dry_run": f"{result_dry_run.status} + {result_dry_run.message}",
                             "number_of_files":result_dry_run.number_of_files_to_download,
                             "total_size_to_download":result_dry_run.total_size,
                             "first_file_to_download":get_filename(result_dry_run),
                             "error":True})
                    try:
                        result_size_file = copernicusmarine.get(dataset_id= dataset.dataset_id,
                                                                dataset_version= version.label,
                                                                dataset_part= part.name,
                                                                filter=f"*{result_dry_run.files[0].filename}*",
                                                                dry_run=True)
                    except Exception as e:
                        dataset_informations_download.append(
                            {"dataset_id": dataset.dataset_id,
                             "dataset_version": version.label,
                             "version_part": part.name,
                             "service_name": service.service_name,
                             "result_dry_run": f"No file",
                             "number_of_files":0,
                             "total_size_to_download":0,
                             "first_file_to_download":"",
                             "error":True,
                             "error_message":"No file associated"})
                        continue
                        
                    if result_size_file.total_size > 2000: #Size is in Mb here
                        dataset_informations_download.append(
                            {"dataset_id": dataset.dataset_id,
                             "dataset_version": version.label,
                             "version_part": part.name,
                             "service_name": service.service_name,
                             "result_dry_run": f"{result_size_file.status} + {result_size_file.message}",
                             "number_of_files":result_size_file.number_of_files_to_download,
                             "total_size_to_download":result_size_file.total_size,
                             "first_file_to_download":get_filename(result_size_file),
                             "error":True,
                             "error_message":"File too big"})
                        continue
                        
                    try:
                        result = copernicusmarine.get(dataset_id= dataset.dataset_id, dataset_version= version.label,
                                                      dataset_part= part.name, output_directory='./',
                                                      filter=f"*{result_dry_run.files[0].filename}*",
                                                      no_directories=True)
                        dataset_informations_download.append(
                            {"dataset_id": dataset.dataset_id,
                             "dataset_version": version.label,
                             "version_part": part.name,
                             "service_name": service.service_name,
                             "result_dry_run": f"{result.status} + {result.message}",
                             "number_of_files":result.number_of_files_to_download,
                             "total_size_to_download":result.total_size,
                             "first_file_to_download":get_filename(result),
                             "error":False,
                             "error_message":""})
                        os.remove(result_dry_run.files[0].filename)
                    except Exception as e:
                        dataset_informations_download.append(
                            {"dataset_id": dataset.dataset_id,
                             "dataset_version": version.label,
                             "version_part": part.name,
                             "service_name": service.service_name,
                             "result_dry_run": f"{result.status} + {result.message}",
                             "number_of_files":result.number_of_files_to_download,
                             "total_size_to_download":result.total_size,
                             "first_file_to_download":'',
                             "error":True,
                             "error_message":e})

df_dry_run = pd.DataFrame(dataset_informations_dry_run)
df_information_download = pd.DataFrame(dataset_informations_download)

df_dry_run.to_csv("get_products_dry_run.csv", index=False)
df_information_download.to_csv("get_products_downloaded.csv", index=True)