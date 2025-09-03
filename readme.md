# Copernicus Marine Data Testing Scripts

This repository contains automated testing scripts designed to monitor and verify the quality and availability of data from the Copernicus Data Store. A more detailed documentation can be found here: https://gkoenig-mercator.github.io/Automation-test-Marine-Data-Store/

## Purpose

The primary focus of these tests is **not** to validate the functionalities of the Copernicus Marine Toolbox commands themselves, but rather to:

- Ensure the **integrity** of the datasets  
- Monitor the **download speed**  
- Verify the **availability** of the latest data

## Current Tests

The initial suite of tests includes:

- Regular checks for the presence of the most recent datasets  (**Implemented**)


## Future Plans

- Automate the delivery of test results in the documentation (**Being implemented**)
- Comparison between current and historical datasets to detect any unintended modifications  (**To be implemented**)
- Measurement and logging of data download speeds  (**To be implemented**)

## Uses and Scripts Descriptions

Most of the script can be run independently. What they do is:

- Add_data_in_database: Takes the data from a csv file containing the tryouts ("downloaded_datasets") of data downloading and puts the results into a database
- check_if_download_errors: Search the downloading csv file ("downloaded_datasets") for datasets that could not be downloaded and return "False" if it finds any
- extracts_datasets_from_describe: Creates a csv file containing all the informations from datasets found with the copernicusmarine.describe command.
- retrieve_from_describe_test_availabilibity_and_push_in_db: Master script that loads the datasets from the describe commands, tries to download them, puts the results into a database and then returns "False" if some datasets were not downloadable
- Test_downloading_datasets: Scan the csv file "list_of_informations_from_the_describe.csv" and tries to download all the data from this csv files
- treating_outputs: Reads the outputs from the csv file "downloaded_datasets" and gives some basic statistics by regions

To run all those scripts, use "python script_name.py --data-dir path_to_storage" where "path_to-storage" is the directory where your results will be stored.

There is an order: 1) retrieve_from_describe_test_availabilibity_and_push_in_db can be run in stand alone
                   2) extracts_datasets_from_describe: Can be run in stand-alone
                   3) Test_downloading_datasets: Requires that extracts_datasets_from_describe has run
                   4) check_if_download_errors: Requires that Test_downloading_datasets has run
                   5) Add_data_in_database: Requires that Test_downloading_datasets has run
                   6) treating_outputs: Requires that Test_downloading_datasets has run

## Database schema and use

So far the database has a simple schema with only one table and a row that contains all the informations about a download, including the errors encountered in case it could not work. Working on a more complex schema is planned.

To access the database, you can use:

psql -h HOST -p PORT -U USERNAME -d DATABASE_NAME

And then for listing the tables:

\dt

And for printing the first ten or last ten rows:

SELECT * FROM my_table LIMIT 10;

SELECT * FROM my_table ORDER BY id DESC LIMIT 10;

## Feedback and Contributions

Your questions, feedback, and suggestions are highly welcome! Please reach out to:

**Guillaume Koenig**  
Email: [gkoenig@mercator-ocean.fr](mailto:gkoenig@mercator-ocean.fr)

Feel free to use, modify, and share these scripts under an open, collaborative spirit.Here are some scripts to automate tests for the data of the Copernicus Data Store.
