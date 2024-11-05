import csv
from netmiko import ConnectHandler
import datetime

# Function to send commands to a device using Netmiko and collect output
def send_commands_to_device(device_info, commands):
    results = []
    try:
        # Set up the device connection parameters
        connection = ConnectHandler(
            device_type=device_info["device_type"],  # Use the correct device type (e.g., 'cisco_ios')
            host=device_info["ip_address"],
            username=device_info["username"],
            password=device_info["password"],
        )

        # Add the logging check command based on device_type
        if device_info["device_type"] == "cisco_ios":
            commands.append("show running-config | include logging facility")
        elif device_info["device_type"] == "juniper":
            commands.append("show configuration system syslog | match facility")
        

        # Send each command and collect output
        for command in commands:
            output = connection.send_command(command)
            results.append({
                "hostname": device_info['hostname'],
                "ip_address": device_info['ip_address'],
                "command": command,
                "output": output
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



# Main function to send commands to all devices and save results
def main():
    devices = read_devices_from_csv('devices.csv')
    commands = [
        "show ip interface brief",
        "show version"
    ]

    all_results = []
    for a_device in devices:
        results = send_commands_to_device(a_device, commands)
        all_results.extend(results)  # Collect all results

    # Write all results to a CSV file with a timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"output_results_{timestamp}.csv"
    write_results_to_csv(all_results, output_filename)

if __name__ == "__main__":
    main()
