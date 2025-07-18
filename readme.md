# Copernicus Marine Data Testing Scripts

This repository contains automated testing scripts designed to monitor and verify the quality and availability of data from the Copernicus Data Store.

## Purpose

The primary focus of these tests is **not** to validate the functionalities of the Copernicus Marine Toolbox commands themselves, but rather to:

- Ensure the **integrity** of the datasets  
- Monitor the **download speed**  
- Verify the **availability** of the latest data

## Current Tests

The initial suite of tests includes:

- Regular checks for the presence of the most recent datasets  
- Comparison between current and historical datasets to detect any unintended modifications  
- Measurement and logging of data download speeds  

## Future Plans

- Automate the delivery of test results via email notifications  
- Implement a database to store historical test results for trend analysis and long-term comparisons  

## Feedback and Contributions

Your questions, feedback, and suggestions are highly welcome! Please reach out to:

**Guillaume Koenig**  
Email: [gkoenig@mercator-ocean.fr](mailto:gkoenig@mercator-ocean.fr)

Feel free to use, modify, and share these scripts under an open, collaborative spirit.Here are some scripts to automate tests for the data of the Copernicus Data Store.

The goal is not to tests the functionalities of the commands themselves as much as it is to control integrity of data, speed of download and availability of data.

The first tests would be:

- Regular testing of presence of latest data
- Comparison of some datasets with their ancient version to see if they have not been modified
- Measurements of download speed

The idea is then to transfer the results of those tests via email. For future comparison purpose, I am considering adding a database to add the tests.

All questions and suggestions should be sent to gkoenig@mercator-ocean.fr. And of course everything is free to be copied.
