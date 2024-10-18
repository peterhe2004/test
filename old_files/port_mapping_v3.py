from jinja2 import Environment, FileSystemLoader
import csv
import os

# Read CSV file into a list of dictionaries
with open('shCDP5.csv', 'r') as f:
    reader = csv.DictReader(f)
    headers = next(reader)
    data = [row for row in reader]



config_directory = "mapping_existing_new"
grouped_data = {}

# Group data by 'sw' field
for row in data:
    headers_added = False
    sw_value = row['sw']
    if sw_value not in grouped_data:
        grouped_data[sw_value] = []
        grouped_data[sw_value].append(row)

    # if not headers_added:
    #     grouped_data[0].extend(headers)
    #     headers_added = True

# Set up Jinja2 environment and load the template
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('port_mapping_v1.j2')

# config exporting directory
if not os.path.exists(config_directory):
    os.mkdir(config_directory)

# Generate separate CSV for each 'sw' group
# def generating_config(sw, group):
#     output_filename = f"{config_directory}/{sw}_mapping.txt"  # Create filename based on 'sw' value
#     with open(f"{config_directory}/{sw}_mapping.txt", 'w', newline='') as f:
#         # f.write(row)

for sw, group in grouped_data.items():
    row = template.render(group=group)
    # generating_config(sw, group)
    with open(f"{config_directory}/{sw}_existing.csv", 'w', newline='') as file:
        # f.write(row)
        writer = csv.writer(file)
        writer.writerow(headers) 
        writer.writerows(data) 
