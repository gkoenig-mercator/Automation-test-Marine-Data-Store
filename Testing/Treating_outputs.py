import pandas as pd
dataset = pd.read_csv("downloaded_datasets.csv")
list_regions = ['Mediterranean','Antarctic', 'Arctic','Iberia-Biscay-Ireland','NorthWestern European Shelf','Atlantic North','Baltic','Black Sea','Global']

for region in list_regions:
    dataset[dataset['region']==region][['last_downloadable_time','last_available_time']].value_counts(dropna=False).to_csv(f'times_{region}.csv')

dataset.groupby(['region', 'coordinate'])['downloadable'].value_counts().reset_index().to_csv('downloadable_datasets_per_coordinate.csv')
