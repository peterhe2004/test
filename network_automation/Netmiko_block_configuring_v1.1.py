import csv
from netmiko import ConnectHandler
from concurrent.futures import ThreadPoolExecutor, as_completed
import keyring
import datetime
import time

def copy_running_to_tftp(connection, tftp_server="192.168.1.1", tftp_path="tftp-root"):
    # Send the copy command
    command = f"copy running-config tftp:{tftp_server}/{tftp_path}"
    output = connection.send_command_timing(command)
    
    # Check if there's a prompt for IP address confirmation
    if "Address or name of remote host" in output:
        output += connection.send_command_timing(tftp_server)  # Send the IP address
    
    # Handle other prompts as needed (e.g., confirmation of filename)
    if "Destination filename" in output:
        output += connection.send_command_timing("\n")  # Press Enter to accept the default filename
    
    return {
        "command": "copy_running_to_tftp",
        "output": output
    }

def configure_logging(connection):
    config_block = [
        "logging host xxxx",
        "logging trap xxxx"
    ]
    output = connection.send_config_set(config_block)
    return {
        "sent_command": "configure_logging",
        "output": output
    }   

def save_configuration(connection):
    config_block = [
        "do copy running-configure startup-configure",
        ""
    ]
    output = connection.send_config_set(config_block)
    return {
        "sent_command": "save_configuration",
        "show_output" : output
    } 

# Function to send a configuration block to a device using Netmiko
def send_configuration_to_device(device_info):
    results = []
    try:
        password = keyring.get_password("network_device", device_info["username"])
        
        # Set up the device connection parameters
        connection = ConnectHandler(
            device_type=device_info["IOS_type"],  # Use the correct device type (e.g., 'cisco_ios')
            host=device_info["ip_address"],
            username=device_info["username"],
            password=password, # Use the retrieved password here
        )

        # Call the configuration blocks
        results.append(copy_running_to_tftp(connection))

        time.sleep(5)

        results.append(configure_logging(connection))

        results.append(save_configuration(connection))
        
        time.sleep(2)
        
        results.append(copy_running_to_tftp(connection))

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
        #fieldnames = ["hostname", "ip_address", "command", "output"]
        writer = csv.writer(csvfile)
        #writer.writeheader()
        writer.writerows(results)
    print(f"Results saved to {filename}")

# Main function to send configuration to all devices and save results
def main():
    devices = read_devices_from_csv('devices_inventory.csv')

    all_results = []

    max_threads = 10  # Adjust based on system resources and device load
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        # Submit each device to the executor
        futures = [executor.submit(send_configuration_to_device, device) for device in devices]

        # Collect results as they complete
        for future in as_completed(futures):
            all_results.append(future.result())

    # for device in devices:
    #     results = send_configuration_to_device(device, config_block)
    #     all_results.extend(results)  # Collect all results

    # Write all results to a CSV file with a timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"output_results_{timestamp}.csv"
    write_results_to_csv(all_results, output_filename)

if __name__ == "__main__":
    main()
