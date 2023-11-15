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

# Read data2
data2 = read_csv('SW_template_mapping.csv')

# Filter out and order WAP and DVR rows from data2
wap_rows_data2 = [row for row in data2 if 'wap' in row.get('device', '').lower()]
dvr_rows_data2 = [row for row in data2 if 'dvr' in row.get('device', '').lower()]

# Process each data1 CSV file individually
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):  # Check if the file is a CSV
        file_path = os.path.join(folder_path, filename)
        data1 = read_csv(file_path)

        # Prepare combined data
        combined_data = []
        wap_index, dvr_index = 0, 0  # To keep track of WAP and DVR rows in data2
        for row1 in data1:
            device_value1 = row1.get('device', '').lower()
            if 'wap' in device_value1 and wap_index < len(wap_rows_data2):
                combined_data.append((row1, wap_rows_data2[wap_index]))
                wap_index += 1
            elif 'dvr' in device_value1 and dvr_index < len(dvr_rows_data2):
                combined_data.append((row1, dvr_rows_data2[dvr_index]))
                dvr_index += 1

        # Render the template
        output = template.render(combined_data=combined_data)

        # Write to a separate output file for this CSV
        with open(os.path.join(folder_path, f'{filename}_output.csv'), 'w') as e:
            e.write(output)
