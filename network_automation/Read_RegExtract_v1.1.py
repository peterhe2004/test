import re
import pandas as pd
from collections import defaultdict


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
    "Te"
)


def extract_interfaces(show_text):

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

        # 排除 AP/Po/Vlan 等接口
        if intf.startswith(EXCLUDED_INTERFACE_PREFIXES):
            continue

        # 只允许 Gi/Fa/Te
        if not intf.startswith(ALLOWED_PORT_TYPES):
            continue

        # 排除 trunk/routed
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

    if not interfaces:
        return ""

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

        # 最后一段

        if start == prev:
            ranges.append(f"{prefix}{start}")

        else:
            ranges.append(f"{prefix}{start}-{prev}")

    return "interface range " + ",".join(ranges)


# =========================
# 主程序
# =========================

INPUT_CSV = "inventory_2.csv"
OUTPUT_CSV = "interface_ranges_output.csv"

SHOW_COL = "show_interface_status"

df = pd.read_csv(INPUT_CSV)

df.columns = df.columns.str.strip()

if SHOW_COL not in df.columns:
    raise SystemExit(
        f"Column '{SHOW_COL}' not found. "
        f"Available columns: {list(df.columns)}"
    )


# 提取接口

df["Filtered_Interfaces"] = df[SHOW_COL].apply(
    lambda x: ",".join(extract_interfaces(x))
)


# 生成 interface range

df["Interface_Range"] = df["show_interface_status"].apply(
    lambda x: make_interface_range(extract_interfaces(x))
)


# 统计接口数量

df["Interface_Count"] = df["Filtered_Interfaces"].apply(
    lambda x: len(x.split(",")) if x else 0
)


df.to_csv(OUTPUT_CSV, index=False)

print(f"Wrote: {OUTPUT_CSV}")