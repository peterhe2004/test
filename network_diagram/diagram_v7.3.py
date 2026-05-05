import re
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


# ==============================
# Device classification function
# ==============================
def get_device_type(node):
    """
    Classify device type based on keywords inside device name.
    The keyword does NOT need to be at the beginning of the name.
    """

    name = str(node).lower()

    # Important: check more specific keywords first
    if "coresw" in name or "core" in name:
        return "CORE"

    elif re.search(r'(^|[-_\s])rt\d*($|[-_\s])', name) or re.search(r'rt\d+', name):
        return "RT"

    elif "stack" in name:
        return "STACK"

    else:
        return "OTHER"


# ==============================
# Hierarchical layout function
# ==============================
def hierarchical_layout(G):
    """
    Place devices by hierarchy:
    RT devices on top,
    coreSW devices in the middle,
    Stack devices at the bottom,
    Other devices scattered left and right.
    """

    layer_y = {
        "RT": 6,
        "CORE": 4,
        "STACK": 2,
        "OTHER": 0,
    }

    groups = {
        "RT": [],
        "CORE": [],
        "STACK": [],
        "OTHER": [],
    }

    for node in G.nodes():
        device_type = get_device_type(node)
        groups[device_type].append(node)

    pos = {}

    for device_type, nodes in groups.items():
        nodes = sorted(nodes)
        y = layer_y[device_type]

        if not nodes:
            continue

        if device_type == "OTHER":
            # Scatter other devices left and right
            for i, node in enumerate(nodes):
                side = -1 if i % 2 == 0 else 1
                x = side * 5
                y_offset = -(i // 2) * 0.8
                pos[node] = (x, y + y_offset)

        else:
            # Spread same-layer devices horizontally
            count = len(nodes)
            spacing = 3
            start_x = -((count - 1) * spacing) / 2

            for i, node in enumerate(nodes):
                x = start_x + i * spacing
                pos[node] = (x, y)

    return pos


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
pos = hierarchical_layout(G)


# ==============================
# Draw graph
# ==============================
plt.figure(figsize=(18, 12))

nx.draw(
    G,
    pos,
    with_labels=True,
    node_color="lightgreen",
    edge_color="gray",
    node_size=2200,
    font_size=12,
)


# ==============================
# Draw edge labels
# MultiGraph needs key-based labels
# ==============================
edge_labels = {}

for u, v, key, data in G.edges(keys=True, data=True):
    edge_labels[(u, v, key)] = (
        f"{u}.{data['SPort']}   <--->   {v}.{data['DPort']}"
    )

nx.draw_networkx_edge_labels(
    G,
    pos,
    edge_labels=edge_labels,
    font_size=8,
)


# ==============================
# Export files
# ==============================
svg_filename = "network_topo_v8_hierarchical.svg"
png_filename = "show_neighbor_topo8_hierarchical.png"

plt.savefig(svg_filename, format="svg", bbox_inches="tight")
plt.savefig(png_filename, format="png", bbox_inches="tight")

print(f"Graph exported to {svg_filename}")
print(f"Graph exported to {png_filename}")