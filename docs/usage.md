# Usage

Most of the scripts can be run independently.  

To run a script:
```bash
python script_name.py --data-dir path_to_storage
Where path_to_storage is the directory where results will be stored.

## Scripts Overview

- add_data_in_database
Takes the data from a CSV file containing download attempts (downloaded_datasets) and inserts results into a database.

- check_if_download_errors
Searches the downloaded_datasets CSV for failed downloads and returns False if any are found.

- extracts_datasets_from_describe
Creates a CSV containing dataset information using the copernicusmarine.describe command.

r- etrieve_from_describe_test_availabilibity_and_push_in_db
Master script. Loads datasets from describe, attempts downloads, stores results in a database, and returns False if downloads fail.

- test_downloading_datasets
Reads list_of_informations_from_the_describe.csv and tries to download all datasets listed.

- treating_outputs
Reads the downloaded_datasets CSV and provides basic statistics by region.

### Execution Order

Some scripts depend on others having been run first:

1. retrieve_from_describe_test_availabilibity_and_push_in_db – standalone

2. extracts_datasets_from_describe – standalone

3. test_downloading_datasets – requires step 2

4. check_if_download_errors – requires step 3

5. add_data_in_database – requires step 3

6. treating_outputs – requires step 3