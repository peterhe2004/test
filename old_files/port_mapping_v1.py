from jinja2 import Environment, FileSystemLoader
import csv
import os

# Read CSV file into a list of dictionaries
with open('shCDP5.csv', 'r') as f:
    reader = csv.DictReader(f)
    data = [row for row in reader]

# Set up Jinja2 environment and load the template
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('port_mapping_v1.j2')

# Render the template
output = template.render(data=data)
e = open(os.path.join("testMapping.csv"), 'w')
e.write(output)