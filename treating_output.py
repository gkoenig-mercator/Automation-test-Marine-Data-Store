import pandas as pd
import os
import argparse

# --- Argument parsing ---
parser = argparse.ArgumentParser(description='Analyze dataset downloadability and timing.')
parser.add_argument('--data-dir', type=str, required=True, help='Path to the directory containing downloaded_datasets.csv')
args = parser.parse_args()

# --- Load dataset ---
csv_path = os.path.join(args.data_dir, "downloaded_datasets.csv")
dataset = pd.read_csv(csv_path)

# --- Define regions ---
list_regions = ['Mediterranean', 'Antarctic', 'Arctic', 'Iberia-Biscay-Ireland',
                'NorthWestern European Shelf', 'Atlantic North', 'Baltic', 'Black Sea', 'Global']

# --- Output time info per region ---
for region in list_regions:
    region_data = dataset[dataset['region'] == region]
    region_data[['last_downloadable_time', 'last_available_time']]\
        .value_counts(dropna=False)\
        .to_csv(os.path.join(args.data_dir, f'times_{region}.csv'))

# --- Calculate percentage of downloadable datasets per region ---
percentage_downloadable = dataset.groupby('region')['downloadable']\
    .value_counts(normalize=True)\
    .mul(100)\
    .rename('percentage')\
    .reset_index()

# Compute overall percentage
total_percentage = dataset['downloadable'].value_counts(normalize=True).mul(100).reset_index()
total_percentage.columns = ['downloadable', 'percentage']
total_percentage['region'] = 'TOTAL'

# Reorder columns to match
total_percentage = total_percentage[['region', 'downloadable', 'percentage']]

# Append the total row(s)
percentage_downloadable = pd.concat([percentage_downloadable, total_percentage], ignore_index=True)

percentage_downloadable.to_csv(os.path.join(args.data_dir, 'percentage_downloadable_per_region.csv'), index=False)


# Create a new column that marks whether times differ
dataset['time_mismatch'] = dataset['last_available_time'] != dataset['last_downloadable_time']

# Compute percentage per region
time_mismatch_percentage = dataset.groupby('region')['time_mismatch']\
    .value_counts(normalize=True)\
    .mul(100)\
    .rename('percentage')\
    .reset_index()

# Compute overall percentage
total_mismatch = dataset['time_mismatch'].value_counts(normalize=True).mul(100).reset_index()
total_mismatch.columns = ['time_mismatch', 'percentage']
total_mismatch['region'] = 'TOTAL'
total_mismatch = total_mismatch[['region', 'time_mismatch', 'percentage']]

# Combine region-wise and total
time_mismatch_percentage = pd.concat([time_mismatch_percentage, total_mismatch], ignore_index=True)

# Save to CSV
time_mismatch_percentage.to_csv(os.path.join(args.data_dir, 'percentage_time_mismatch_per_region.csv'), index=False)