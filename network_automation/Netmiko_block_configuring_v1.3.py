import csv
import re
import keyring
import datetime
import time

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import unified_diff
from netmiko import ConnectHandler


EXCLUDED_VLANS = (
    "trunk",
    "routed",
    "routed-port"
)

EXCLUDED_INTERFACE_PREFIXES = (
    "Ap",
    "Po",
    "Vl",
    "Lo",
    "Nu",
    "Mgmt"
)

ALLOWED_PORT_TYPES = (
    "Gi",
    "Fa",
    "Te",
    "Twe",
    "Fo"
)


def get_running_config(connection):
    return connection.send_command("show running-config")


def extract_non_trunk_non_routed_interfaces(show_text):
    show_text = str(show_text).replace("\\n", "\n")

    pattern = re.compile(
        r'^(?P<intf>\S+)\s+.*?\s+'
        r'(?P<status>connected|notconnect|disabled|err-disabled)\s+'
        r'(?P<vlan>\S+)\s+',
        re.MULTILINE | re.IGNORECASE
    )

    interfaces = []

    for m in pattern.finditer(show_text):
        intf = m.group("intf")
        vlan = m.group("vlan").lower()

        if intf.startswith(EXCLUDED_INTERFACE_PREFIXES):
            continue

        if not intf.startswith(ALLOWED_PORT_TYPES):
            continue

        if vlan in EXCLUDED_VLANS:
            continue

        if "routed" in vlan:
            continue

        interfaces.append(intf)

    return interfaces


def normalize_interface(intf):
    match = re.match(r'^([A-Za-z]+)([\d/]+/)(\d+)$', intf)

    if not match:
        return None

    prefix = match.group(1) + match.group(2)
    port = int(match.group(3))

    return prefix, port


def make_interface_range(interfaces):
    groups = defaultdict(list)

    for intf in interfaces:
        parsed = normalize_interface(intf)

        if parsed:
            prefix, port = parsed
            groups[prefix].append(port)

    ranges = []

    for prefix, ports in groups.items():
        ports = sorted(set(ports))

        if not ports:
            continue

        start = prev = ports[0]

        for port in ports[1:]:
            if port == prev + 1:
                prev = port
            else:
                if start == prev:
                    ranges.append(f"{prefix}{start}")
                else:
                    ranges.append(f"{prefix}{start}-{prev}")

                start = prev = port

        if start == prev:
            ranges.append(f"{prefix}{start}")
        else:
            ranges.append(f"{prefix}{start}-{prev}")

    if not ranges:
        return ""

    return "interface range " + ",".join(ranges)


def copy_running_to_tftp(connection, tftp_server="192.168.1.1", tftp_path="tftp-root"):
    command = f"copy running-config tftp:{tftp_server}/{tftp_path}"
    output = connection.send_command_timing(command)

    if "Address or name of remote host" in output:
        output += connection.send_command_timing(tftp_server)

    if "Destination filename" in output:
        output += connection.send_command_timing("\n")

    return {
        "command": "copy_running_to_tftp",
        "output": output
    }


def push_config(connection):
    show_output = connection.send_command("show interface status")

    interfaces = extract_non_trunk_non_routed_interfaces(show_output)
    range_cmd = make_interface_range(interfaces)

    if not range_cmd:
        return {
            "command": "push_config",
            "interfaces": "",
            "range_cmd": "",
            "output": "No valid non-trunk, non-routed access interfaces found. No config pushed."
        }

    config_block = [
        range_cmd,
        "description USER_PORT",
        "spanning-tree portfast"
    ]

    output = connection.send_config_set(config_block)

    return {
        "command": "push_config",
        "interfaces": ",".join(interfaces),
        "range_cmd": range_cmd,
        "output": output
    }


def save_configuration(connection):
    output = connection.save_config()

    return {
        "command": "save_configuration",
        "output": output
    }


def send_configuration_to_device(device_info):
    results = []

    hostname = device_info.get("hostname", "")
    ip_address = device_info.get("ip_address", "")

    try:
        password = keyring.get_password("network_device", device_info["username"])

        connection = ConnectHandler(
            device_type=device_info.get("IOS_type", "cisco_ios"),
            host=ip_address,
            username=device_info["username"],
            password=password,
        )

        running_config_before = get_running_config(connection)

        results.append({
            "hostname": hostname,
            "ip_address": ip_address,
            **copy_running_to_tftp(connection)
        })

        time.sleep(3)

        push_result = push_config(connection)
        results.append({
            "hostname": hostname,
            "ip_address": ip_address,
            **push_result
        })

        save_result = save_configuration(connection)
        results.append({
            "hostname": hostname,
            "ip_address": ip_address,
            **save_result
        })

        time.sleep(3)

        results.append({
            "hostname": hostname,
            "ip_address": ip_address,
            **copy_running_to_tftp(connection)
        })

        running_config_after = get_running_config(connection)

        diff = unified_diff(
            running_config_before.splitlines(),
            running_config_after.splitlines(),
            fromfile="Before",
            tofile="After",
            lineterm=""
        )

        diff_output = "\n".join(list(diff))

        results.append({
            "hostname": hostname,
            "ip_address": ip_address,
            "command": "configuration_diff",
            "interfaces": push_result.get("interfaces", ""),
            "range_cmd": push_result.get("range_cmd", ""),
            "output": diff_output
        })

        connection.disconnect()

    except Exception as e:
        print(f"Failed to connect to {hostname} ({ip_address}): {e}")

        results.append({
            "hostname": hostname,
            "ip_address": ip_address,
            "command": "Error",
            "interfaces": "",
            "range_cmd": "",
            "output": str(e)
        })

    return results


def read_devices_from_csv(filename):
    devices = []

    with open(filename, "r", newline="", encoding="utf-8-sig") as csvfile:
        csvreader = csv.DictReader(csvfile)

        for row in csvreader:
            row = {k.strip(): v.strip() for k, v in row.items()}
            devices.append(row)

    return devices


def write_results_to_csv(results, filename):
    flattened = []

    for device_results in results:
        for item in device_results:
            flattened.append({
                "hostname": item.get("hostname", ""),
                "ip_address": item.get("ip_address", ""),
                "command": item.get("command", ""),
                "interfaces": item.get("interfaces", ""),
                "range_cmd": item.get("range_cmd", ""),
                "output": item.get("output", "")
            })

    fieldnames = [
        "hostname",
        "ip_address",
        "command",
        "interfaces",
        "range_cmd",
        "output"
    ]

    with open(filename, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flattened)

    print(f"Results saved to {filename}")


def main():
    devices = read_devices_from_csv("devices_inventory.csv")

    all_results = []

    max_threads = 10

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [
            executor.submit(send_configuration_to_device, device)
            for device in devices
        ]

        for future in as_completed(futures):
            all_results.append(future.result())

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"output_results_{timestamp}.csv"

    write_results_to_csv(all_results, output_filename)


if __name__ == "__main__":
    main()