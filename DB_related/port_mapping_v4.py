from jinja2 import Environment, FileSystemLoader
import csv
import os

# Read CSV file into a list of dictionaries
with open('shCDP5.csv', 'r') as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames
    data = [row for row in reader]

config_directory = "mapping_existing_new"
grouped_data = {}

# Group data by 'sw' field
for row in data:
    sw_value = row['sw']
    if sw_value not in grouped_data:
        grouped_data[sw_value] = []
    grouped_data[sw_value].append(row)

# config exporting directory
if not os.path.exists(config_directory):
    os.mkdir(config_directory)

# Generate separate CSV for each 'sw' group
for sw, group in grouped_data.items():
    with open(f"{config_directory}/{sw}_existing.csv", 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader() 
        writer.writerows(group)
