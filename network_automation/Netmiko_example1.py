import csv
from netmiko import ConnectHandler

# Function to send commands to a device using Netmiko
def send_commands_to_device(device_info, commands):
    try:
        # Set up the device connection parameters
        connection = ConnectHandler(
            device_type=device_info["device_type"],  # Use the correct device type (e.g., 'cisco_ios')
            host=device_info["ip_address"],
            username=device_info["username"],
            password=device_info["password"],
        )

        # Send each command and collect output
        for command in commands:
            output = connection.send_command(command)
            print(f"Output for {device_info['hostname']} ({device_info['ip_address']}):\n{output}\n")

        # Close the connection
        connection.disconnect()
    except Exception as e:
        print(f"Failed to connect to {device_info['hostname']} ({device_info['ip_address']}): {e}")

# Read devices from CSV
def read_devices_from_csv(filename):
    devices = []
    with open(filename, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            row['device_type'] = 'cisco_ios'  # Set the device type based on the devices you’re working with
            devices.append(row)
    return devices

# Main function to send commands to all devices
def main():
    devices = read_devices_from_csv('devices.csv')
    commands = [
        "show ip interface brief",
        "show version"
    ]

    for device in devices:
        send_commands_to_device(device, commands)

if __name__ == "__main__":
    main()
