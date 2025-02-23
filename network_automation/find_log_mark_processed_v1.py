import csv
from netmiko import ConnectHandler
from concurrent.futures import ThreadPoolExecutor, as_completed
import keyring
import datetime
import time
import re

# ✅ Read devices from CSV, ensuring 'mitigated' is read correctly
def read_devices_from_csv(filename):
    devices = []
    with open(filename, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            row['device_type'] = 'cisco_ios'  # Set the device type
            row['mitigated'] = row.get('mitigated', 'False') == 'True'  # Convert string to boolean
            devices.append(row)
    return devices

# ✅ Securely retrieve credentials
def get_cred(device: dict):
    return {
        'ip': device['IP_Address'],
        'username': 'usr',
        'password': keyring.get_password("company", "usr"),
    }

# ✅ Count occurrences of a keyword in the output
def count_keyword(input_text, keyword):
    if not isinstance(input_text, str):  # Ensure input is a string
        input_text = " ".join(input_text)  # Convert list to string
    matches = re.findall(rf"(?i)\b{keyword}\b", input_text)  # Case-insensitive whole-word match
    return len(matches)

# ✅ Retrieve running configuration
def get_running_config(connection):
    return connection.send_command("show running-config")

# ✅ Process each device, apply config, and return results
def send_configuration_to_device(device):
    """Processes a network device, applies configuration, and returns results."""
    result = {
        "hostname": device["hostname"],
        "IP_Address": device["IP_Address"],
        "mitigated": device["mitigated"],  # Initial status
        "status": "Skipped" if device["mitigated"] else "Processed",
        "error": ""
    }

    try:
        # Skip if already mitigated
        if device["mitigated"]:
            print(f"Skipping {device['hostname']} ({device['IP_Address']}), already mitigated.")
            return result  # ✅ Return dictionary, NOT a list

        print(f"Processing {device['hostname']} ({device['IP_Address']})...")

        # Establish connection
        connection = ConnectHandler(**get_cred(device))

        # Retrieve configuration
        running_config = get_running_config(connection)

        # Count occurrences of a keyword (example: "YES")
        count = count_keyword(running_config, "YES")
        print(f"Keyword 'YES' appears {count} times in {device['hostname']}")

        # ✅ Mark device as mitigated
        device["mitigated"] = True
        result["status"] = "Mitigated"
        result["mitigated"] = True

    except Exception as e:
        print(f"Failed to connect to {device['hostname']} ({device['IP_Address']}): {e}")
        result["status"] = "Error"
        result["error"] = str(e)

    return result  # ✅ Always return a dictionary

# ✅ Write results to CSV safely
def write_results_to_csv(results, filename):
    if not results:
        print(f"⚠️ No results to write for {filename}. Skipping file creation.")
        return

    # ✅ Ensure the first item is a dictionary before accessing .keys()
    first_valid_result = next((r for r in results if isinstance(r, dict)), None)
    if first_valid_result is None:
        print(f"⚠️ No valid dictionary entries in results. Skipping file creation.")
        return

    fieldnames = list(first_valid_result.keys())  # ✅ Get fieldnames from a valid dictionary

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()  # Write headers

        for row in results:
            if isinstance(row, dict):  # ✅ Ensure row is a dictionary
                if "mitigated" in row:
                    row["mitigated"] = str(row["mitigated"])  # Convert boolean to string
                writer.writerow(row)
            else:
                print(f"⚠️ Skipping unexpected data type in results: {type(row)}")

    print(f"✅ Updated file saved to {filename}")

# ✅ Main function to process devices
def main():
    devices = read_devices_from_csv('devices_inventory.csv')

    # ✅ Filter out already mitigated devices
    devices_to_process = [device for device in devices if not device['mitigated']]
    
    if not devices_to_process:
        print("✅ All devices are already mitigated. No work needed!")
        return  # Exit early if everything is mitigated

    all_results = []
    max_threads = 10  # Adjust based on system resources

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(send_configuration_to_device, device): device for device in devices_to_process}

        # Collect results as they complete
        for future in as_completed(futures):
            device_result = future.result()
            if isinstance(device_result, dict):  # ✅ Ensure only dictionaries are added
                all_results.append(device_result)
            else:
                print(f"⚠️ Unexpected result type from thread: {type(device_result)} - Skipping")

    # ✅ Save updated mitigation status to `devices_inventory.csv`
    write_results_to_csv(devices, 'devices_inventory.csv')

    # ✅ Save actual output results for logging
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"output_results_{timestamp}.csv"
    write_results_to_csv(all_results, output_filename)

if __name__ == "__main__":
    main()
