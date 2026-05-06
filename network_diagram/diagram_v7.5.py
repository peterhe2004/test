import re
from collections import defaultdict

import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


def get_device_type(node):
    name = str(node).lower()

    if "coresw" in name or "core" in name:
        return "CORE"
    elif re.search(r'(^|[-_\s])rt\d*($|[-_\s])', name) or re.search(r'rt\d+', name):
        return "RT"
    elif "stack" in name:
        return "STACK"
    else:
        return "OTHER"


def build_device_side_map(edge_data):
    side_map = {}

    for _, row in edge_data.iterrows():
        side = str(row.get("device_side", "")).upper()

        if side not in ["A", "B"]:
            side = "UNKNOWN"

        if pd.notna(row["Source"]):
            side_map[row["Source"]] = side

        if pd.notna(row["Target"]):
            side_map[row["Target"]] = side

    return side_map


def hierarchical_layout(G):
    layer_y = {
        "RT": 6,
        "CORE": 4,
        "STACK": 2,
        "OTHER": 0,
    }

    layer_x = {
        "A": -6,
        "B": 6,
        "UNKNOWN": 0,
    }

    groups = { }

    for node in G.nodes():
        dev_type = get_device_type(node)
        side = side_map.get(node, "UNKNOWN")

        key = (dev_type, side)

        if key not in groups:
            groups[key] = []

        groups[key].append(node)

    pos = {}

    for (device_type, side), nodes in groups.items():
        nodes = sorted(nodes)

        base_y = layer_y[device_type]
        base_x = layer_x[side]

        spacing_y = 0.8
        spacing_x = 2.5

        for i, node in enumerate(nodes):
            x = base_x + spacing_x * (i % 3 - 1 )
            y = base_y + spacing_y * (i // 3)

            pos[node] = (x, y)

        # if not nodes:
        #     continue
        #
        # if device_type == "OTHER":
        #     for i, node in enumerate(nodes):
        #         side = -1 if i % 2 == 0 else 1
        #         x = side * 6
        #         y_offset = -(i // 2) * 0.8
        #         pos[node] = (x, y + y_offset)
        # else:
        #     spacing = 3
        #     count = len(nodes)
        #     start_x = -((count - 1) * spacing) / 2
        #
        #     for i, node in enumerate(nodes):
        #         x = start_x + i * spacing
        #         pos[node] = (x, y)

    return pos


def draw_curved_edges_with_labels(G, pos):
    edge_groups = defaultdict(list)

    for u, v, key, data in G.edges(keys=True, data=True):
        pair = tuple(sorted([u, v]))
        edge_groups[pair].append((u, v, key, data))

    for pair, edges in edge_groups.items():
        total_edges = len(edges)

        for i, (u, v, key, data) in enumerate(edges):
            rad = (i - (total_edges - 1) / 2) * 0.35

            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=[(u, v)],
                edge_color="gray",
                connectionstyle=f"arc3,rad={rad}",
                arrows=False,
            )

            # Manual label position following the curve approximately
            x1, y1 = pos[u]
            x2, y2 = pos[v]

            xm = (x1 + x2) / 2
            ym = (y1 + y2) / 2

            dx = x2 - x1
            dy = y2 - y1
            length = (dx ** 2 + dy ** 2) ** 0.5

            if length == 0:
                continue

            offset_x = -dy / length * rad * 2.5
            offset_y = dx / length * rad * 2.5

            label_x = xm + offset_x
            label_y = ym + offset_y

            label = f"{u}.{data['SPort']}  <--->  {v}.{data['DPort']}"

            plt.text(
                label_x,
                label_y,
                label,
                fontsize=8,
                ha="center",
                va="center",
                bbox=dict(
                    facecolor="white",
                    edgecolor="none",
                    alpha=0.7,
                    boxstyle="round,pad=0.2",
                ),
            )


# ==============================
# Read CSV file
# ==============================
edge_data = pd.read_csv("shCDP5.csv")

print("CSV Data Preview:")
print(edge_data.head())


# ==============================
# Create graph
# ==============================
G = nx.MultiGraph()

print("\nAdding edges to the graph:")

edge_id = 0

for index, row in edge_data.iterrows():
    if pd.notna(row["Target"]):
        source = row["Source"]
        target = row["Target"]

        print(
            f"Adding edge: {source} -> {target} "
            f"with SPort: {row['SPort']} and DPort: {row['DPort']}"
        )

        G.add_edge(
            source,
            target,
            key=edge_id,
            SPort=row["SPort"],
            DPort=row["DPort"],
            status=row["status"],
        )

        edge_id += 1

    else:
        print(f"Skipping row {index} due to missing Target.")


# ==============================
# Apply hierarchical layout
# ==============================

side_map = build_device_side_map(edge_data)
pos = hierarchical_layout(G, side_map)


# ==============================
# Draw graph
# ==============================
plt.figure(figsize=(20, 14))

nx.draw_networkx_nodes(
    G,
    pos,
    node_color="lightgreen",
    node_size=2400,
)

nx.draw_networkx_labels(
    G,
    pos,
    font_size=11,
)

draw_curved_edges_with_labels(G, pos)


# ==============================
# Export files
# ==============================
plt.axis("off")

svg_filename = "network_topo_v9_curved.svg"
png_filename = "show_neighbor_topo9_curved.png"

plt.savefig(svg_filename, format="svg", bbox_inches="tight")
plt.savefig(png_filename, format="png", bbox_inches="tight")

print(f"Graph exported to {svg_filename}")
print(f"Graph exported to {png_filename}")