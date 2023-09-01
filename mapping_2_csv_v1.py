import csv
from jinja2 import Environment, FileSystemLoader

def read_csv(filename, filter_value):
    data = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['device'] == filter_value:
                data.append(row)
    return data

# Read data from CSV files, filtering only rows where device == "WAP"
data1 = read_csv('csv1.csv', 'WAP')
data2 = read_csv('csv2.csv', 'WAP')

# Prepare combined data
combined_data = zip(data1, data2)

# Setup Jinja2
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('template.j2')

# Render the template
output = template.render(combined_data=combined_data)
print(output)
