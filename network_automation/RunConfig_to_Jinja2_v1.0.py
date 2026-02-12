import csv
from ciscoconfparse import CiscoConfParse

def export_config_to_csv(config_path, csv_output):
    parse = CiscoConfParse(config_path, syntax='ios')
    
    # We only want to inventory interfaces that actually have IP addresses
    interfaces = parse.find_objects_w_child(parentspec=r"^interface", childspec=r"ip address")
    
    inventory_data = []

    for intf in interfaces:
        # Extract the interface name (e.g., GigabitEthernet1/0/1)
        name = intf.re_match_field(r"^interface\s+(.*)")
        
        # Extract IP and Mask
        ip_line = intf.re_search_children(r"ip address")[0].text.strip()
        # Regex to split 'ip address 10.1.1.1 255.255.255.0' into parts
        ip_parts = ip_line.split()
        ip_addr = ip_parts[2]
        mask = ip_parts[3]
        
        # Extract VRF (if it exists)
        vrf_search = intf.re_search_children(r"vrf forwarding")
        vrf_name = vrf_search[0].text.strip().split()[-1] if vrf_search else "Global"

        inventory_data.append({
            'interface': name,
            'ip_address': ip_addr,
            'subnet_mask': mask,
            'vrf': vrf_name
        })

    # Write to CSV
    keys = ['interface', 'ip_address', 'subnet_mask', 'vrf']
    with open(csv_output, 'w', newline='') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(inventory_data)

    print(f"Inventory successfully exported to {csv_output}")

# Run it
export_config_to_csv('cisco_9300_running_config.conf', 'switch_inventory.csv')