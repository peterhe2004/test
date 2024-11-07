import csv
from netmiko import ConnectHandler
import datetime

# Function to send a configuration block to a device using Netmiko
def send_configuration_to_device(device_info, config_block):
    results = []
    try:
        # Set up the device connection parameters
        connection = ConnectHandler(
            device_type=device_info["device_type"],  # Use the correct device type (e.g., 'cisco_ios')
            host=device_info["ip_address"],
            username=device_info["username"],
            password=device_info["password"],
        )

        # Send the configuration block
        output = connection.send_config_set(config_block)
        results.append({
            "hostname": device_info['hostname'],
            "ip_address": device_info['ip_address'],
            "command": "configuration_block",
            "output": output
        })

        # Check for "logging facility local" based on device_type
        if device_info["device_type"] == "cisco_ios":
            check_output = connection.send_command("show running-config | include logging facility")
        elif device_info["device_type"] == "juniper":
            check_output = connection.send_command("show configuration system syslog | match facility")
        else:
            check_output = "Command not defined for this device type"
        
        results.append({
            "hostname": device_info['hostname'],
            "ip_address": device_info['ip_address'],
            "command": "logging facility check",
            "output": check_output
        })

        # Close the connection
        connection.disconnect()
    except Exception as e:
        print(f"Failed to connect to {device_info['hostname']} ({device_info['ip_address']}): {e}")
        results.append({
            "hostname": device_info['hostname'],
            "ip_address": device_info['ip_address'],
            "command": "Error",
            "output": str(e)
        })

    return results

# Read devices from CSV
def read_devices_from_csv(filename):
    devices = []
    with open(filename, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            row['device_type'] = 'cisco_ios'  # Set the device type based on the devices you’re working with
            devices.append(row)
    return devices

# Write results to an output CSV
def write_results_to_csv(results, filename="output_results.csv"):
    # Write headers and rows
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ["hostname", "ip_address", "command", "output"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"Results saved to {filename}")

# Main function to send configuration to all devices and save results
def main():
    devices = read_devices_from_csv('devices.csv')
    
    # Configuration block (paragraph) to be applied to each device
    config_block = [
        "logging buffered 10000",
        "no logging console",
        "logging trap warnings",
        "logging facility local4",
        # Add more configuration lines as needed
    ]

    all_results = []
    for device in devices:
        results = send_configuration_to_device(device, config_block)
        all_results.extend(results)  # Collect all results

    # Write all results to a CSV file with a timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"output_results_{timestamp}.csv"
    write_results_to_csv(all_results, output_filename)

if __name__ == "__main__":
    main()
