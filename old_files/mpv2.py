import csv
import os
import pandas as pd
from jinja2 import Environment, FileSystemLoader

folder_path = r'C:\Users\phe\Documents\tech\test\mapping_existing'

def read_csv(filename, filter_value):
    data = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            device_value = row.get('device', '').lower()
            if filter_value.lower() in device_value:
                data.append(row)
    return data

# Setup Jinja2
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('mapping_2_csv_v2.j2')

# Read data from CSV files, filtering only rows where device == "WAP"
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):  # Check if the file is a CSV
        file_path = os.path.join(folder_path, filename)           
        data1 = read_csv(file_path, 'WAP')
        data2 = read_csv('SW_template_mapping.csv', 'WAP')

        # Prepare combined data
        combined_data = zip(data1, data2)

        # Render the template
        output = template.render(combined_data=combined_data)
        print(output)

        with open(os.path.join(folder_path, f'{filename}_output.csv'), 'w') as e:
            e.write(output)