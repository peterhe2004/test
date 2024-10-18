import csv
import os
from jinja2 import Environment, FileSystemLoader

folder_path = r'C:\\Users\\phe\\Documents\\tech\\test\\mapping_existing'

def read_csv(filename):
    data = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

# Setup Jinja2
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('mpv3.j2')

# Read data from SW_template_mapping.csv
data2 = read_csv('SW_template_mapping.csv')

# List of device types to filter by (can be expanded or modified)
device_types = ['wap', 'dvr', 'atm', 'printer']  # Add more devices here as needed

# Process each CSV file in folder_path
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        data1 = read_csv(file_path)

        # Prepare combined data with all ports included
        combined_data = []
        device_indices = {device_type: 0 for device_type in device_types}  # Track indices for each device type

        


        for row1 in data1:
            device_mapped = False
            for device_type in device_types:
                device_rows = [row for row in data2 if device_type in row.get('device', '').lower()]
                if device_type in row1.get('device', '').lower() and device_indices[device_type] < len(device_rows):
                    combined_data.append((row1, device_rows[device_indices[device_type]]))
                    device_indices[device_type] += 1
                    device_mapped = True
                    break
                

            if not device_mapped:
                # For ports in data1 not mapping to specified devices, add them with an empty mapping
                combined_data.append((row1, {}))
        
        added_ports = [row1['port'] for row1, _ in combined_data if 'port' in row1]

        #Prepare a dictionary with device type as key and filtered rows as value
        device_filtered_rows = {device_type: [row for row in data2 if device_type in row.get('device', '').lower()] for device_type in device_types}

        # Adding all unmapped ports from data2 to the combined data
        for row2 in data2:
            if row2['port'] not in added_ports:
            # if not any(row2 in device_rows for device_type, device_rows in device_filtered_rows.items() if device_type in row2.get('device', '').lower()):
                combined_data.append(({}, row2))
                added_ports.append(row2['port']) 

        # Render the template with combined data
        output = template.render(combined_data=combined_data)

        # Write to a separate output file for this CSV
        with open(os.path.join(folder_path, f'{filename}_output.csv'), 'w') as e:
            e.write(output)
