import csv
import os
from jinja2 import Environment, FileSystemLoader

folder_path = r'C:\Users\phe\Documents\tech\test\mapping_existing'

def read_csv(filename):
    data = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

# Setup Jinja2
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('mapping_2_csv_v2.j2')

# List of filter values
filter_values = ['WAP1', 'WAP2', 'DVR', 'printer']  # Updated to include WAP1 and WAP2

# Read data2
data2 = read_csv('SW_template_mapping.csv')

# Process each data1 CSV file individually
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):  # Check if the file is a CSV
        file_path = os.path.join(folder_path, filename)
        data1 = read_csv(file_path)

        # Prepare combined data
        combined_data = []
        for row1 in data1:
            device_value1 = row1.get('device', '').lower()
            if device_value1 in [fv.lower() for fv in filter_values]:
                for row2 in data2:
                    device_value2 = row2.get('device', '').lower()
                    if device_value1 == device_value2:
                        combined_data.append((row1, row2))
                        break  # Stop after the first exact match

        # Render the template
        output = template.render(combined_data=combined_data)

        # Write to a separate output file for this CSV
        with open(os.path.join(folder_path, f'{filename}_output.csv'), 'w') as e:
            e.write(output)
