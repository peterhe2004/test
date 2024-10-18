import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

# Read the CSV file with edge attributes (Source, Target, SPort, DPort, and Status)
edge_data = pd.read_csv('shCDP5.csv')
print("CSV Data Preview:")
print(edge_data.head())

# Create a new MultiGraph to allow multiple edges between nodes
G = nx.MultiGraph()

# Add edges with attributes (such as SPort and DPort), skipping rows with missing Target
print("\nAdding edges to the graph:")
for index, row in edge_data.iterrows():
    if pd.notna(row['Target']):  # Skip rows where Target is NaN
        print(f"Adding edge: {row['Source']} -> {row['Target']} with SPort: {row['SPort']} and DPort: {row['DPort']}")
        G.add_edge(row['Source'], row['Target'], SPort=row['SPort'], DPort=row['DPort'], status=row['status'])
    else:
        print(f"Skipping row {index} due to missing Target.")

# Define the graph layout
pos = {}

# Group the data by source, so that each source network is drawn in blocks
grouped_data = edge_data.dropna(subset=['Source', 'Target']).groupby('Source')

# Calculate initial y positions
total_sources = len(grouped_data)
y_source = total_sources * 3  # Multiply by 3 to ensure enough spacing
y_target = total_sources * 3

x_source = -1  # Fixed x-coordinate for source nodes (left side)
x_target = 1   # Fixed x-coordinate for target nodes (right side)

# print("\nAssigning node positions:")
for source, group in grouped_data:
    # print(f"Processing group for source: {source}")
    for index, row in group.iterrows():
        source = row['Source']
        target = row['Target']
        
        # If source node not already placed, place it on the left
        if source not in pos:
            pos[source] = (x_source, y_source)
            # print(f"Positioning source {source} at ({x_source}, {y_source})")
            y_source -= 1  # Decrement the y-position for the next source node
        
        # If target node not already placed, place it on the right
        if target not in pos:
            pos[target] = (x_target, y_target)
            # print(f"Positioning target {target} at ({x_target}, {y_target})")
            y_target -= 1  # Decrement the y-position for the next target node
        # else:
        #     # Adjust target position if multiple connections to the same target node exist
        #     pos[target] = (x_target, y_target - 0.2)  # Small shift to avoid overlap

    # After processing the current source group, leave extra space between networks
    y_source -= 5  # Add a gap between source networks
    y_target -= 2  # Add a gap between target networks

# Make the diagram larger
plt.figure(figsize=(15, 11))
# pos = nx.spring_layout(G)  # Use spring layout for visualization

# Draw the graph with custom node positions, allowing for multiple edges
nx.draw(G, pos, with_labels=True, node_color='lightgreen', edge_color='gray', node_size=2000, font_size=14)

# Extract and format the edge labels (showing Source.Port <-> Target.Port)
# edge_labels = {(row['Source'], row['Target'], index): f"{row['SPort']} <---> {row['DPort']}" for index, row in edge_data.iterrows() if pd.notna(row['Target'])}
edge_labels = {(row['Source'], row['Target']): f"{str(row['Source']) + '.' + str(row['SPort']) + '   <--->  ' + str(row['Target']) + '.' + str(row['DPort'])}" for index, row in edge_data.iterrows() if pd.notna(row['Target'])}

# Draw the edge labels on the graph
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

# Export the graph to GraphML format
# graphml_filename = "network_topo_v7.graphml"
# nx.write_graphml(G, graphml_filename)
# print(f"Graph exported to {graphml_filename}")

# Show the plot
plt.savefig('show_neighbor_topo7.png')
# plt.show(block=True)

