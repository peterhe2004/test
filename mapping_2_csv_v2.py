import csv
from jinja2 import Environment, FileSystemLoader

def read_csv(filename, filter_value):
    data = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if filter_value.lower() in row['device'].lower():
                data.append(row)
    return data

# Read data from CSV files, filtering only rows where device == "WAP"
data1 = read_csv('101_mapping.csv', 'WAP')
data2 = read_csv('102_mapping.csv', 'WAP')

# Prepare combined data
combined_data = zip(data1, data2)

# Setup Jinja2
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('mapping_2_csv_v2.j2')

# Render the template
output = template.render(combined_data=combined_data)
print(output)
e = open("Mapping_2_output.csv", 'w')
e.write(output)