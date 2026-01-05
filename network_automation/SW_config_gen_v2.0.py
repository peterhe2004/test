import csv
import os
from jinja2 import Environment, FileSystemLoader

def generate_configs(csv_filename, template_filename):
    # 1. Set up Jinja2 environment to look in the current directory
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template_filename)

    if not os.path.exists(csv_filename):
        print(f"Error: {csv_filename} not found.")
        return

    with open(csv_filename, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Map CSV columns to template variables
            # We pass the entire 'row' dictionary to the template
            config_output = template.render(
                hostname=row['Hostname'],
                loop_ip=row['Loop_IP'],
                mgmt_ip=row['Mgmt_IP'],
                site=row['Site']
            )

            # Define output filename
            file_name = f"{row['Site']}_{row['Hostname']}.conf"
            
            with open(file_name, 'w') as out_file:
                out_file.write(config_output)
            
            print(f"Generated config for: {row['Hostname']}")

if __name__ == "__main__":
    generate_configs('IPschema_Test_v1.csv', 'switch_template.j2')