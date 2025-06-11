import copernicusmarine
import re
import date_handling

list_products = copernicusmarine.describe()

list_names = []
list_id = []
list_last_dates = []

def extract_last_date(string_with_last_available_date):
    
    # Regular expression to extract the last date
    last_date_pattern = r"\b(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:[+-]\d{2}:\d{2})?)"

    # Find all matches and extract the last date
    matches = re.findall(last_date_pattern, string_with_last_available_date)
    if matches:
        last_date = matches[-1]  # Get the last match
        return last_date
    else:
        print("No dates found.")
        return None

for i in range(len(list_products.products)):
    for j in range(len(list_products.products[i].datasets)):
        list_names.append(list_products.products[i].datasets[j].dataset_name)
        list_id.append(list_products.products[i].datasets[j].dataset_id)

for id in list_id:
    try :
        copernicusmarine.subset(dataset_id=id,
                                start_datetime="2026-01-01T00:00:00",
                                end_datetime="2026-01-31T23:59:59",
                                )
        list_last_dates.append('')
    except Exception as e:
        exception_message = str(e)
        print("Exception Message:", exception_message)
        last_date = extract_last_date(exception_message)
        last_date = date_handling.shift_date(last_date, 0)
        list_last_dates.append(last_date)
        
        date_one_day_before = date_handling.shift_date(last_date, -1)
        copernicusmarine.subset(dataset_id=id,
                                start_datetime=date_one_day_before,
                                end_datetime=last_date,
                                )
        
        
        
        
print(list_last_dates)

