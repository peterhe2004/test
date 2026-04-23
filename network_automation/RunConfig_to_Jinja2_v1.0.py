import csv
from ciscoconfparse import CiscoConfParse

def export_config_to_csv(config_path, csv_output):
    parse = CiscoConfParse(config_path, syntax='ios')
    
    # We loop through ALL interfaces now to ensure we don't skip any
    interfaces = parse.find_objects(r"^interface")
    
    interface_data = []

    for intf in interfaces:
        # 1. RESET variables at the start of every loop to prevent "ghost" data
        ip_addr = "N/A"
        mask = "N/A"
        vrf_name = "Global"
        status = "Up"

        # 2. Extract Interface Name
        name = intf.re_match_typed(r'^interface\s+(.*)', default='Unknown')

        # 3. Check for Shutdown status
        if intf.has_child_with(r'shutdown'):
            status = "Shutdown"

        # 4. Extract IP and Mask safely
        ip_children = intf.re_search_children(r"ip address")
        if ip_children:
            ip_line = ip_children[0].text.strip()
            parts = ip_line.split()
            
            if len(parts) >= 4:
                ip_addr = parts[2]
                mask = parts[3]
            elif "dhcp" in parts:
                ip_addr = "DHCP"
                mask = "DHCP"
            elif "negotiated" in parts:
                ip_addr = "Negotiated"
                mask = "Negotiated"

        # 5. Extract VRF
        vrf_children = intf.re_search_children(r"vrf forwarding")
        if vrf_children:
            vrf_name = vrf_children[0].text.strip().split()[-1]

        interface_data.append({
            'interface': name,
            'ip_address': ip_addr,
            'subnet_mask': mask,
            'vrf': vrf_name,
            'status': status
        })

    # Write to CSV with the new 'status' column
    keys = ['interface', 'ip_address', 'subnet_mask', 'vrf', 'status']
    with open(csv_output, 'w', newline='') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(interface_data)

    print(f"Clean inventory exported to {csv_output}")


def export_routing_to_csv(config_path, csv_output):
    parse = CiscoConfParse(config_path, syntax='ios')
    routing_inventory = []

    # --- 1. HANDLE EIGRP (Including Named/AF mode) ---
    eigrp_blocks = parse.find_objects(r"^router eigrp")
    for eigrp in eigrp_blocks:
        # Get the EIGRP instance name/AS
        eigrp_id = eigrp.re_match_typed(r'^router eigrp\s+(\S+)', default='Unknown')
        
        # Check for Address Families (like in your 2911 config)
        af_blocks = eigrp.re_search_children(r"^ address-family")
        
        if af_blocks:
            for af in af_blocks:
                af_type = af.re_match_typed(r'^ address-family\s+(.*)', default='Unknown')
                
                # Find details inside this specific Address Family
                # We search for network statements or redistribution
                details = af.re_search_children(r"^\s+(network|redistribute)")
                for d in details:
                    routing_inventory.append({
                        'Protocol': 'EIGRP',
                        'Instance_AS': eigrp_id,
                        'Context': af_type,
                        'Configuration': d.text.strip()
                    })
        else:
            # Traditional EIGRP (Flat structure)
            details = eigrp.re_search_children(r"^ (network|redistribute)")
            for d in details:
                routing_inventory.append({
                    'Protocol': 'EIGRP',
                    'Instance_AS': eigrp_id,
                    'Context': 'Global',
                    'Configuration': d.text.strip()
                })

    # --- 2. HANDLE BGP ---
    bgp_blocks = parse.find_objects(r"^router bgp")
    for bgp in bgp_blocks:
        bgp_as = bgp.re_match_typed(r'^router bgp\s+(\d+)', default='Unknown')
        
        # BGP can have neighbors globally OR in Address Families
        # Global neighbors/networks
        global_details = bgp.re_search_children(r"^ (neighbor|network)")
        for gd in global_details:
            routing_inventory.append({
                'Protocol': 'BGP',
                'Instance_AS': bgp_as,
                'Context': 'Global',
                'Configuration': gd.text.strip()
            })

        # BGP Address Families
        bgp_af_blocks = bgp.re_search_children(r"^ address-family")
        for af in bgp_af_blocks:
            af_type = af.re_match_typed(r'^ address-family\s+(.*)', default='Unknown')
            af_details = af.re_search_children(r"^\s+(neighbor|network|aggregate-address)")
            for ad in af_details:
                routing_inventory.append({
                    'Protocol': 'BGP',
                    'Instance_AS': bgp_as,
                    'Context': af_type,
                    'Configuration': ad.text.strip()
                })

    # Write to CSV
    keys = ['Protocol', 'Instance_AS', 'Context', 'Configuration']
    with open(csv_output, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(routing_inventory)

    print(f"Routing inventory saved to {csv_output}")


export_config_to_csv('c2911-router.conf', 'switch_inventory_fixed.csv')
export_routing_to_csv('c2911-router.conf', 'routing_inventory.csv')