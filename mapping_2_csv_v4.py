import csv
import os
from jinja2 import Environment, FileSystemLoader

folder_path = r'C:\Users\phe\Documents\tech\test\mapping_existing'

def read_csv_to_dict(filename, filter_values, unique_id_column):
    data = {}
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            device_value = row.get('device', '').lower()
            for filter_value in filter_values:
                if filter_value.lower() in device_value:
                    unique_id = row.get(unique_id_column)
                    if unique_id:
                        data[unique_id] = row
                    break
    return data

# Setup Jinja2
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('mapping_2_csv_v2.j2')

# List of filter values and unique identifier column name
filter_values = ['WAP', 'DVR', 'printer']
unique_id_column = 'port'  # Replace with your actual unique identifier column name

# Read data from CSV files
data1 = {}
data2 = {}
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):  # Check if the file is a CSV
        file_path = os.path.join(folder_path, filename)
        data1.update(read_csv_to_dict(file_path, filter_values, unique_id_column))

data2.update(read_csv_to_dict('SW_template_mapping.csv', filter_values, unique_id_column))

# Match and combine data
combined_data = []
for unique_id, row1 in data1.items():
    row2 = data2.get(unique_id)
    if row2:
        combined_data.append((row1, row2))

# Render the template
output = template.render(combined_data=combined_data)
print(output)

with open(os.path.join(folder_path, 'combined_output.csv'), 'w') as e:
    e.write(output)
