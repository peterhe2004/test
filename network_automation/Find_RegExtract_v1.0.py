import re
from collections import defaultdict

def extract_non_trunk_interfaces(show_text):
    show_text = str(show_text).replace("\\n", "\n")

    pattern = re.compile(
        r'^(?P<intf>\S+)\s+.*?\s+(?P<status>connected|notconnect|disabled|err-disabled)\s+(?P<vlan>\S+)\s+',
        re.MULTILINE | re.IGNORECASE
    )

    interfaces = []

    for m in pattern.finditer(show_text):
        intf = m.group("intf")
        vlan = m.group("vlan")

        if vlan.lower() != "trunk":
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

    return "interface range " + ",".join(ranges)