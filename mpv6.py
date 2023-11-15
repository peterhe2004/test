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
            unique_id = row.get(unique_id_column)
            if unique_id and any(filter_value.lower() in device_value for filter_value in filter_values):
                data[unique_id] = row
    return data

# Setup Jinja2
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('mapping_2_csv_v2.j2')

# List of filter values and unique identifier column name
filter_values = ['WAP', 'DVR', 'printer']
unique_id_column = 'port'  # Replace with your actual unique identifier column name

# Read data2
data2 = read_csv_to_dict('SW_template_mapping.csv', filter_values, unique_id_column)

# Process each data1 CSV file individually
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):  # Check if the file is a CSV
        file_path = os.path.join(folder_path, filename)
        data1 = read_csv_to_dict(file_path, filter_values, unique_id_column)

        # Debugging: Print the number of rows read from each file
        print(f"Rows read from {filename}: {len(data1)}")
        print(f"Rows in data2: {len(data2)}")

        # Match and combine data
        combined_data = []
        for unique_id, row1 in data1.items():
            row2 = data2.get(unique_id)
            if row2:
                combined_data.append((row1, row2))
            else:
                # Debugging: Print unmatched unique IDs
                print(f"Unmatched ID in {filename}: {unique_id}")

        # Render the template
        output = template.render(combined_data=combined_data)

        # Debugging: Check if combined data is empty
        if not combined_data:
            print(f"No matching data found for {filename}")

        # Write to a separate output file for this CSV
        with open(os.path.join(folder_path, f'{filename}_output.csv'), 'w') as e:
            e.write(output)
