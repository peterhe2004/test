import re
import glob
import os
import networkx as nx
import matplotlib.pyplot as plt


INPUT_PATTERN = "* sh cdp nei.txt"
SITE_PREFIX_LEN = 4


def normalize_device_name(name):
    return name.split(".")[0]


def normalize_interface(intf):
    return intf.replace(" ", "")


def format_interface(device, intf):
    return f"{device}_{normalize_interface(intf)}"


def get_site_name(device_name):
    return device_name[:SITE_PREFIX_LEN]


def get_short_device_name(device_name):
    """
    AAAA_coreSW -> coreSW
    BBBB_sub-sw1 -> sub-sw1
    """
    if "_" in device_name:
        return device_name.split("_", 1)[1]
    return device_name


def get_node_color(node):
    n = node.lower()

    if "core" in n:
        return "#4A90E2"
    elif "wan" in n:
        return "#F5A623"
    elif "sub" in n:
        return "#7ED321"
    else:
        return "#B8B8B8"


def get_edge_color(u, v):
    if "wan" in u.lower() or "wan" in v.lower():
        return "#F5A623"
    elif "core" in u.lower() or "core" in v.lower():
        return "#4A90E2"
    else:
        return "#555555"


def get_local_device_from_filename(file_path):
    """
    AAAA_coreSW sh cdp nei.txt -> AAAA_coreSW
    """
    base = os.path.basename(file_path)
    return base.split(" sh cdp nei.txt")[0]


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


def deduplicate_links(links):
    seen = set()
    unique_links = []

    for link in links:
        key = make_link_key(link)
        if key not in seen:
            seen.add(key)
            unique_links.append(link)

    return unique_links


def build_site_groups():
    site_files = {}

    for file_path in glob.glob(INPUT_PATTERN):
        local_device = get_local_device_from_filename(file_path)
        site = get_site_name(local_device)

        site_files.setdefault(site, [])
        site_files[site].append(file_path)

    return site_files


def get_layout_for_site(site, nodes):
    """
    Use short names to place devices, but keep full site-prefixed names in graph.
    """
    pos = {}

    for node in nodes:
        short = get_short_device_name(node)

        if short == "coreSW":
            pos[node] = (0, 0)
        elif short == "sub-sw1":
            pos[node] = (0, 1.8)
        elif short == "sub-sw2":
            pos[node] = (-1.8, -0.8)
        elif short == "WAN-1":
            pos[node] = (1.8, -0.8)
        else:
            pos[node] = (0, -1.8)

    return pos


def draw_site_topology(site, links):
    unique_links = deduplicate_links(links)

    print(f"\n===== Site {site} unique links =====")
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

    pos = get_layout_for_site(site, G.nodes())

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
        labels={node: node for node in G.nodes()},
        font_size=11,
        font_weight="bold"
    )

    edge_count = {}

    for u, v, key, data in G.edges(keys=True, data=True):
        short_pair = tuple(sorted([
            get_short_device_name(u),
            get_short_device_name(v)
        ]))

        index = edge_count.get(short_pair, 0)
        edge_count[short_pair] = index + 1

        if short_pair == ("coreSW", "sub-sw1"):
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
        short_pair = tuple(sorted([
            get_short_device_name(u),
            get_short_device_name(v)
        ]))

        index = label_count.get(short_pair, 0)
        label_count[short_pair] = index + 1

        x1, y1 = pos[u]
        x2, y2 = pos[v]

        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2

        label = (
            f'{format_interface(u, data["local_interface"])}\n'
            f'↔\n'
            f'{format_interface(v, data["remote_interface"])}'
        )

        if short_pair == ("coreSW", "sub-sw1"):
            label_x = mx - 0.42 if index == 0 else mx + 0.42
            label_y = my
        elif "WAN-1" in short_pair:
            label_x = mx + 0.15
            label_y = my + 0.18
        elif "sub-sw2" in short_pair:
            label_x = mx - 0.15
            label_y = my + 0.18
        else:
            label_x = mx
            label_y = my + 0.12

        plt.text(
            label_x,
            label_y,
            label,
            fontsize=8,
            color=get_edge_color(u, v),
            ha="center",
            va="center",
            bbox=dict(
                facecolor="white",
                edgecolor="none",
                alpha=0.85,
                boxstyle="round,pad=0.25"
            )
        )

    plt.title(f"CDP Network Topology - Site {site}", fontsize=15, fontweight="bold")
    plt.axis("off")
    plt.tight_layout()

    output_file = f"{site}_topology.png"
    plt.savefig(output_file, dpi=200)
    plt.close()

    print(f"Saved topology image: {output_file}")


def main():
    site_files = build_site_groups()

    for site, files in sorted(site_files.items()):
        site_links = []

        print(f"\nProcessing site {site}:")
        for file_path in sorted(files):
            local_device = get_local_device_from_filename(file_path)
            print(f"  - {file_path} as {local_device}")
            site_links.extend(parse_cdp_file(file_path, local_device))

        draw_site_topology(site, site_links)


if __name__ == "__main__":
    main()