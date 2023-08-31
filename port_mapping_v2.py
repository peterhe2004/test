from jinja2 import Environment, FileSystemLoader
import csv
import os

# Read CSV file into a list of dictionaries
with open('shCDP5.csv', 'r') as f:
    reader = csv.DictReader(f)
    data = [row for row in reader]

grouped_data = {}

# Group data by 'sw' field
for row in data:
    sw_value = row['sw']
    if sw_value not in grouped_data:
        grouped_data[sw_value] = []
    grouped_data[sw_value].append(row)

# Set up Jinja2 environment and load the template
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('port_mapping_plan.j2')


# Generate separate CSV for each 'sw' group
for sw, group in grouped_data.items():
    output_filename = f"{sw}_mapping.csv"  # Create filename based on 'sw' value
    with open(output_filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['sw', 'port', 'status', 'device'])
        writer.writeheader()
        for row in group:
            writer.writerow(row)
