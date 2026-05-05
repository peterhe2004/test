import re
import glob
import os
import matplotlib
matplotlib.use('Agg')   # 👈 解决 tkinter 问题（关键）

import matplotlib.pyplot as plt
import networkx as nx


INPUT_PATTERN = "* sh cdp nei.txt"
SITE_PREFIX_LEN = 4


# =========================
# 基础工具函数
# =========================

def normalize_device_name(name):
    return name.split(".")[0]


def normalize_interface(intf):
    return intf.replace(" ", "")


def format_interface(device, intf):
    return f"{device}_{normalize_interface(intf)}"


def get_site_name(device_name):
    return device_name[:SITE_PREFIX_LEN]


def get_short_device_name(device_name):
    if "_" in device_name:
        return device_name.split("_", 1)[1]
    return device_name


# =========================
# 设备分类（用于层级布局）
# =========================

def classify_node(node):
    short = get_short_device_name(node).lower()

    if "core" in short:
        return "core"
    elif "wan" in short:
        return "wan"
    elif "sub" in short or "sw" in short:
        return "access"
    else:
        return "other"


def spread_nodes(nodes, y, x_gap=2.8):
    nodes = sorted(nodes)

    if not nodes:
        return {}

    count = len(nodes)
    start_x = -((count - 1) * x_gap) / 2

    pos = {}

    for i, node in enumerate(nodes):
        x = start_x + i * x_gap
        pos[node] = (x, y)

    return pos


def get_layout_for_site(site, nodes):
    layers = {
        "access": [],
        "core": [],
        "wan": [],
        "other": [],
    }

    for node in nodes:
        role = classify_node(node)
        layers[role].append(node)

    pos = {}

    # Access layer (top)
    pos.update(spread_nodes(layers["access"], y=2.2))

    # Core layer (middle)
    pos.update(spread_nodes(layers["core"], y=0.0))

    # WAN layer (bottom)
    pos.update(spread_nodes(layers["wan"], y=-2.2))

    # Other (very bottom)
    pos.update(spread_nodes(layers["other"], y=-4.0))

    return pos


# =========================
# 颜色策略
# =========================

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


# =========================
# CDP 解析
# =========================

def get_local_device_from_filename(file_path):
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
                or line.startswith("Total")
                or line.startswith(local_device + "#")
            ):
                continue

            match = re.match(
                r"^(?P<neighbor>\S+)\s+"
                r"(?P<local_intf>[A-Za-z]+\s*\S+)\s+"
                r"\d+\s+.+?\s+"
                r"\S+\s+"
                r"(?P<remote_intf>[A-Za-z]+\s*\S+)$",
                line
            )

            if not match:
                continue

            neighbor = normalize_device_name(match.group("neighbor"))

            if neighbor == local_device:
                continue

            links.append({
                "source": local_device,
                "target": neighbor,
                "local_interface": match.group("local_intf"),
                "remote_interface": match.group("remote_intf"),
            })

    return links


# =========================
# 去重（关键逻辑）
# =========================

def make_link_key(link):
    ep1 = f'{link["source"]}:{normalize_interface(link["local_interface"])}'
    ep2 = f'{link["target"]}:{normalize_interface(link["remote_interface"])}'
    return tuple(sorted([ep1, ep2]))


def deduplicate_links(links):
    seen = set()
    unique = []

    for link in links:
        key = make_link_key(link)
        if key not in seen:
            seen.add(key)
            unique.append(link)

    return unique


# =========================
# 拓扑绘图
# =========================

def draw_site_topology(site, links):
    links = deduplicate_links(links)

    G = nx.MultiGraph()

    for link in links:
        G.add_edge(
            link["source"],
            link["target"],
            local_interface=link["local_interface"],
            remote_interface=link["remote_interface"],
        )

    pos = get_layout_for_site(site, G.nodes())

    plt.figure(figsize=(12, 8))

    # Nodes
    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=3500,
        node_color=[get_node_color(n) for n in G.nodes()],
        edgecolors="black"
    )

    # Labels (full name)
    nx.draw_networkx_labels(
        G,
        pos,
        labels={n: n for n in G.nodes()},
        font_size=9
    )

    # Edges
    edge_count = {}

    for u, v, key, data in G.edges(keys=True, data=True):
        pair = tuple(sorted([u, v]))
        idx = edge_count.get(pair, 0)
        edge_count[pair] = idx + 1

        rad = 0.2 if idx == 0 else -0.2 if pair[0] != pair[1] else 0

        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=[(u, v)],
            connectionstyle=f"arc3,rad={rad}",
            width=2,
            edge_color=get_edge_color(u, v)
        )

    # Edge Labels（手动绘制，避免覆盖）
    label_count = {}

    for u, v, key, data in G.edges(keys=True, data=True):
        pair = tuple(sorted([u, v]))
        idx = label_count.get(pair, 0)
        label_count[pair] = idx + 1

        x1, y1 = pos[u]
        x2, y2 = pos[v]

        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2

        offset = 0.4 if idx == 0 else -0.4

        label = (
            f'{format_interface(u, data["local_interface"])}\n↔\n'
            f'{format_interface(v, data["remote_interface"])}'
        )

        plt.text(
            mx + offset,
            my,
            label,
            fontsize=7,
            ha="center",
            va="center",
            color=get_edge_color(u, v),
            bbox=dict(facecolor="white", alpha=0.8, edgecolor="none")
        )

    plt.title(f"Topology - {site}")
    plt.axis("off")

    outfile = f"{site}_topology.png"
    plt.savefig(outfile, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"Generated: {outfile}")


# =========================
# 主流程
# =========================

def main():
    site_files = {}

    for file_path in glob.glob(INPUT_PATTERN):
        device = get_local_device_from_filename(file_path)
        site = get_site_name(device)

        site_files.setdefault(site, [])
        site_files[site].append(file_path)

    for site, files in sorted(site_files.items()):
        links = []

        print(f"\nProcessing site: {site}")

        for f in files:
            dev = get_local_device_from_filename(f)
            links.extend(parse_cdp_file(f, dev))

        draw_site_topology(site, links)


if __name__ == "__main__":
    main()