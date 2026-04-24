import re
import networkx as nx
import matplotlib.pyplot as plt


files = {
    "sub-sw1": "sub-sw1 sh cdp nei.txt",
    "coreSW": "coreSW sh cdp nei.txt",
    "WAN-1": "WAN-1 sh cdp nei.txt",
    "sub-sw2": "sub-sw2 sh cdp nei.txt",
}


def normalize_device_name(name):
    """
    Remove domain name:
    sub-sw1.cisco.com -> sub-sw1
    """
    return name.split(".")[0]


def normalize_interface(intf):
    """
    Normalize interface format:
    Eth 0/1 -> Eth0/1
    Gi1/0/1 -> Gi1/0/1
    """
    return intf.replace(" ", "")


def parse_cdp_file(file_path, local_device):
    links = []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            if (
                line.startswith("Device ID")
                or line.startswith("Capability")
                or line.startswith("S - Switch")
                or line.startswith("Total")
            ):
                continue

            match = re.match(
                r"^(?P<neighbor>\S+)\s+"
                r"(?P<local_intf>[A-Za-z]+\s*\S+)\s+"
                r"(?P<holdtime>\d+)\s+"
                r"(?P<capability>.+?)\s+"
                r"(?P<platform>\S+)\s+"
                r"(?P<remote_intf>[A-Za-z]+\s*\S+)$",
                line
            )

            if not match:
                continue

            neighbor = normalize_device_name(match.group("neighbor"))

            # Skip self-loop
            if neighbor == local_device:
                print(f"Skip self-loop: {local_device} -> {neighbor}")
                continue

            links.append({
                "source": local_device,
                "target": neighbor,
                "local_interface": match.group("local_intf"),
                "remote_interface": match.group("remote_intf"),
            })

    return links


def make_link_key(link):
    """
    Deduplicate bidirectional CDP records.

    Example:
    coreSW Eth0/1 <-> WAN-1 Eth0
    WAN-1 Eth0   <-> coreSW Eth0/1

    These should be treated as one physical link.
    """
    a = link["source"]
    b = link["target"]

    a_intf = normalize_interface(link["local_interface"])
    b_intf = normalize_interface(link["remote_interface"])

    endpoint_1 = f"{a}:{a_intf}"
    endpoint_2 = f"{b}:{b_intf}"

    return tuple(sorted([endpoint_1, endpoint_2]))


# Parse all files
all_links = []

for local_device, file_path in files.items():
    all_links.extend(parse_cdp_file(file_path, local_device))


# Deduplicate physical links
seen = set()
unique_links = []

for link in all_links:
    key = make_link_key(link)

    if key not in seen:
        seen.add(key)
        unique_links.append(link)


print("\nFinal unique links:")
for link in unique_links:
    print(
        f'{link["source"]} {link["local_interface"]} '
        f'<-> {link["target"]} {link["remote_interface"]}'
    )


# Build graph
G = nx.MultiGraph()

for link in unique_links:
    G.add_edge(
        link["source"],
        link["target"],
        local_interface=link["local_interface"],
        remote_interface=link["remote_interface"],
    )


# Fixed layout for clearer topology
pos = {
    "coreSW": (0, 0),
    "sub-sw1": (0, 1.8),
    "sub-sw2": (-1.8, -0.8),
    "WAN-1": (1.8, -0.8),
}


plt.figure(figsize=(10, 7))

nx.draw_networkx_nodes(G, pos, node_size=3000)
nx.draw_networkx_labels(G, pos, font_size=11, font_weight="bold")


# Draw edges, including parallel links
edge_count = {}

for u, v, key, data in G.edges(keys=True, data=True):
    pair = tuple(sorted([u, v]))
    index = edge_count.get(pair, 0)
    edge_count[pair] = index + 1

    if pair == ("coreSW", "sub-sw1"):
        rad = 0.18 if index == 0 else -0.18
    else:
        rad = 0.0

    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=[(u, v)],
        connectionstyle=f"arc3,rad={rad}",
        width=2
    )


# Edge labels
# edge_labels = {}
#
# for u, v, key, data in G.edges(keys=True, data=True):
#     label = f'{data["local_interface"]} ↔ {data["remote_interface"]}'
#     edge_labels[(u, v)] = label
#
# nx.draw_networkx_edge_labels(
#     G,
#     pos,
#     edge_labels=edge_labels,
#     font_size=8
# )


# Draw edge labels manually, supports parallel links
for u, v, key, data in G.edges(keys=True, data=True):
    label = f'{data["local_interface"]} ↔ {data["remote_interface"]}'

    x1, y1 = pos[u]
    x2, y2 = pos[v]

    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2

    pair = tuple(sorted([u, v]))

    if pair == ("coreSW", "sub-sw1"):
        # 给两条平行链路的标签不同偏移，避免重叠
        if key == 0:
            label_x = mx - 0.28
            label_y = my
        else:
            label_x = mx + 0.28
            label_y = my
    else:
        label_x = mx
        label_y = my + 0.08

    plt.text(
        label_x,
        label_y,
        label,
        fontsize=8,
        ha="center",
        va="center",
        rotation=90 if pair == ("coreSW", "sub-sw1") else 0,
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.7)
    )


plt.title("CDP Network Topology")
plt.axis("off")
plt.tight_layout()
plt.show()