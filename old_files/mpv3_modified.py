
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
template = env.get_template('mpv3.j2')

# Read data from SW_template_mapping.csv
all_port_data = read_csv('SW_template_mapping.csv')

# Process each CSV file in folder_path
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        data1 = read_csv(file_path)

        # Prepare data for the template
        # Here, we'll pass all port data irrespective of their mapping status
        # If specific processing is needed, it can be added here

        # Render the template with all port data
        output = template.render(ports=all_port_data)
        print(output)
