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
    return name.split(".")[0]


def normalize_interface(intf):
    return intf.replace(" ", "")


def format_interface(device, intf):
    return f"{device}_{normalize_interface(intf)}"


def get_node_color(node):
    node_lower = node.lower()

    if "core" in node_lower:
        return "#4A90E2"      # core switch - blue
    elif "wan" in node_lower:
        return "#F5A623"      # WAN/router - orange
    elif "sub" in node_lower:
        return "#7ED321"      # access/sub switch - green
    else:
        return "#B8B8B8"      # unknown - gray


def get_edge_color(u, v):
    u_lower = u.lower()
    v_lower = v.lower()

    if "wan" in u_lower or "wan" in v_lower:
        return "#F5A623"
    elif "core" in u_lower or "core" in v_lower:
        return "#4A90E2"
    else:
        return "#555555"


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
                or line.startswith(local_device + "#")
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
    endpoint_1 = f'{link["source"]}:{normalize_interface(link["local_interface"])}'
    endpoint_2 = f'{link["target"]}:{normalize_interface(link["remote_interface"])}'

    return tuple(sorted([endpoint_1, endpoint_2]))


all_links = []

for local_device, file_path in files.items():
    all_links.extend(parse_cdp_file(file_path, local_device))


seen = set()
unique_links = []

for link in all_links:
    key = make_link_key(link)

    if key not in seen:
        seen.add(key)
        unique_links.append(link)


print("\nFinal unique links:")
for idx, link in enumerate(unique_links, start=1):
    print(
        f'{idx}. '
        f'{format_interface(link["source"], link["local_interface"])} '
        f'<-> '
        f'{format_interface(link["target"], link["remote_interface"])}'
    )


G = nx.MultiGraph()

for idx, link in enumerate(unique_links, start=1):
    G.add_edge(
        link["source"],
        link["target"],
        link_id=idx,
        local_interface=link["local_interface"],
        remote_interface=link["remote_interface"],
    )


pos = {
    "coreSW": (0, 0),
    "sub-sw1": (0, 1.8),
    "sub-sw2": (-1.8, -0.8),
    "WAN-1": (1.8, -0.8),
}


plt.figure(figsize=(12, 8))

nx.draw_networkx_nodes(
    G,
    pos,
    node_size=3500,
    node_color=[get_node_color(node) for node in G.nodes()],
    edgecolors="black",
    linewidths=1.5
)

nx.draw_networkx_labels(
    G,
    pos,
    font_size=11,
    font_weight="bold"
)


edge_count = {}

for u, v, key, data in G.edges(keys=True, data=True):
    pair = tuple(sorted([u, v]))
    index = edge_count.get(pair, 0)
    edge_count[pair] = index + 1

    if pair == ("coreSW", "sub-sw1"):
        rad = 0.22 if index == 0 else -0.22
    else:
        rad = 0.0

    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=[(u, v)],
        connectionstyle=f"arc3,rad={rad}",
        width=2.5,
        edge_color=get_edge_color(u, v)
    )


label_count = {}

for u, v, key, data in G.edges(keys=True, data=True):
    pair = tuple(sorted([u, v]))
    index = label_count.get(pair, 0)
    label_count[pair] = index + 1

    x1, y1 = pos[u]
    x2, y2 = pos[v]

    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2

    label = (
        f'{format_interface(u, data["local_interface"])}\n'
        f'↔\n'
        f'{format_interface(v, data["remote_interface"])}'
    )

    if pair == ("coreSW", "sub-sw1"):
        label_x = mx - 0.38 if index == 0 else mx + 0.38
        label_y = my
        rotation = 0
    elif "WAN-1" in pair:
        label_x = mx + 0.1
        label_y = my + 0.18
        rotation = 0
    elif "sub-sw2" in pair:
        label_x = mx - 0.1
        label_y = my + 0.18
        rotation = 0
    else:
        label_x = mx
        label_y = my + 0.12
        rotation = 0

    plt.text(
        label_x,
        label_y,
        label,
        fontsize=8,
        color=get_edge_color(u, v),
        ha="center",
        va="center",
        rotation=rotation,
        bbox=dict(
            facecolor="white",
            edgecolor="none",
            alpha=0.8,
            boxstyle="round,pad=0.25"
        )
    )


plt.title("CDP Network Topology", fontsize=15, fontweight="bold")
plt.axis("off")
plt.tight_layout()
plt.show()