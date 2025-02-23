import csv
from netmiko import ConnectHandler
from concurrent.futures import ThreadPoolExecutor, as_completed
import keyring
import datetime
import time
import re

def get_running_config(connection):
    return connection.send_command("show running-config")


def get_cred(device : dict):
    cred = {
        'ip' : device['IP_Address'],
        'password' : keyring.get_password("company", "usr"),
        'username' : 'usr'
        }
    return cred


def count_keyword(input, keyword):
    matches = re.findall(rf"(?i)\b{keyword}\b", input)
    return len(matches)


# Function to send a configuration block to a device using Netmiko
def send_configuration_to_device(device):
    results = []
    try:
        password = keyring.get_password("network_device", device["username"])
        
        # Set up the device connection parameters
        connection = ConnectHandler(**get_cred(device))
        
        results.append(get_running_config(connection))
        count = count_keyword(results, "YES")
        print(count)
        results.append("count of SVI", {count})

    except Exception as e:
        print(f"Failed to connect to {device['hostname']} ({device['ip_address']}): {e}")
        results.append({
            "hostname": device['hostname'],
            "ip_address": device['ip_address'],
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