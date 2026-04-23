import csv
from ciscoconfparse import CiscoConfParse

def export_full_inventory(config_path, csv_output):
    parse = CiscoConfParse(config_path, syntax='ios')
    combined_data = []

    # --- PART 1: INTERFACE EXTRACTION ---
    interfaces = parse.find_objects(r"^interface")
    for intf in interfaces:
        ip_addr, mask, vrf_name, status = "N/A", "N/A", "Global", "Up"
        name = intf.re_match_typed(r'^interface\s+(.*)', default='Unknown')

        if intf.has_child_with(r'shutdown'):
            status = "Shutdown"

        ip_children = intf.re_search_children(r"ip address")
        if ip_children:
            parts = ip_children[0].text.strip().split()
            if len(parts) >= 4:
                ip_addr, mask = parts[2], parts[3]
            elif "dhcp" in parts:
                ip_addr = mask = "DHCP"
            elif "negotiated" in parts:
                ip_addr = mask = "Negotiated"

        vrf_children = intf.re_search_children(r"vrf forwarding")
        if vrf_children:
            vrf_name = vrf_children[0].text.strip().split()[-1]

        combined_data.append({
            'Type': 'Interface',
            'Primary_ID': name,
            'Detail_1': ip_addr,
            'Detail_2': mask,
            'Context/VRF': vrf_name,
            'Status': status
        })

    # --- PART 2: ROUTING EXTRACTION ---
    routers = parse.find_objects(r"^router (eigrp|bgp)")
    for router in routers:
        proto_match = router.re_match_typed(r'^router\s+(\S+)', default='Unknown')
        as_id = router.re_match_typed(r'^router\s+\S+\s+(\S+)', default='Unknown')
        
        af_blocks = router.re_search_children(r"^ address-family")
        if af_blocks:
            for af in af_blocks:
                af_type = af.re_match_typed(r'^ address-family\s+(.*)', default='Unknown')
                details = af.re_search_children(r"^\s+(network|neighbor|redistribute)")
                for d in details:
                    combined_data.append({
                        'Type': f'Routing ({proto_match.upper()})',
                        'Primary_ID': as_id,
                        'Detail_1': d.text.strip(),
                        'Detail_2': 'N/A',
                        'Context/VRF': af_type,
                        'Status': 'N/A'
                    })
        else:
            details = router.re_search_children(r"^ (network|neighbor|redistribute)")
            for d in details:
                combined_data.append({
                    'Type': f'Routing ({proto_match.upper()})',
                    'Primary_ID': as_id,
                    'Detail_1': d.text.strip(),
                    'Detail_2': 'N/A',
                    'Context/VRF': 'Global',
                    'Status': 'N/A'
                })

    # --- PART 3: ACL EXTRACTION ---
    # Catching: 'access-list 100...', 'ip access-list...', and 'ipv6 access-list...'
    acl_parents = parse.find_objects(r"^((ip|ipv6) )?access-list")
    
    for acl in acl_parents:
        # Determine ACL type and Name/Number
        raw_text = acl.text.strip()
        
        if raw_text.startswith('access-list'):
            # Numbered ACL: 'access-list 101 permit...'
            parts = raw_text.split()
            acl_id = parts[1]
            acl_type = "Numbered ACL"
            # In numbered ACLs, the rule is on the same line
            rule = " ".join(parts[2:])
            combined_data.append({
                'Type': acl_type,
                'Primary_ID': acl_id,
                'Detail_1': rule,
                'Detail_2': 'N/A',
                'Context/VRF': 'N/A',
                'Status': 'N/A'
            })
        else:
            # Named ACL: 'ip access-list extended NAME'
            # The rules are children lines
            acl_id = raw_text.split()[-1]
            acl_type = f"Named {raw_text.split()[0].upper()} ACL"
            
            rules = acl.children
            for r in rules:
                combined_data.append({
                    'Type': acl_type,
                    'Primary_ID': acl_id,
                    'Detail_1': r.text.strip(),
                    'Detail_2': 'N/A',
                    'Context/VRF': 'N/A',
                    'Status': 'N/A'
                })

    # --- PART 4: FINAL WRITE ---
    keys = ['Type', 'Primary_ID', 'Detail_1', 'Detail_2', 'Context/VRF', 'Status']
    with open(csv_output, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(combined_data)

    print(f"Full unified inventory (Inc. ACLs) saved to {csv_output}")

export_full_inventory('c2911-router.conf', 'unified_network_audit.csv')