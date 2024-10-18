import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


# Read the CSV file with edge attributes (Source, Target, and Weight)
edge_data = pd.read_csv('shCDP5.csv')

# Create a new graph
G = nx.Graph()

# Add edges with attributes (such as weight)
for index, row in edge_data.iterrows():
    if pd.notna(row['Target']):  # Ensure the 'Targets' are not NaN
           G.add_edge(row['Source'], row['Target'], SPort=row['SPort'], DPort=row['DPort'])
    # G.add_edge(row['Source'], row['Target'], Source=row['Source'], SPort=row['SPort'], Target=row['Target'], DPort=row['DPort'])

# Define the graph layout (optional but makes it look cleaner)
#pos = nx.spring_layout(G)
#pos = nx.circular_layout(G)
pos = nx.shell_layout(G)

# Create a position dictionary for node placementpos = {}
pos = {}

# Group the data by source, so that each source network is drawn in blocks
grouped_data = edge_data.dropna(subset=['Source', 'Target']).groupby('Source')

# Calculate initial y positions
total_sources = len(grouped_data)
y_source = total_sources * 3  # Multiply by 2 to ensure enough spacing
y_target = total_sources * 3
    
# Assign source nodes to the left and target nodes to the right
x_source = -1  # Fixed x-coordinate for source nodes (left side)
x_target = 1   # Fixed x-coordinate for target nodes (right side)

# y_source = len(edge_data)  # Initial y-coordinate for source nodes (incremental)
# y_target = len(edge_data)  # Initial y-coordinate for target nodes (incremental)


for source, group in grouped_data:
    for index, row in group.iterrows():
        source = row['Source']
        target = row['Target']
        
        #If source node not already placed, place it on the left
        if source not in pos:
            pos[source] = (x_source, y_source)
            y_source -= 1  # Increment the y-position for the next source node
        #If target node not already placed, place it on the right
        if target not in pos:
            pos[target] = (x_target, y_target)
            y_target -= 1  # Increment the y-position for the next target node

    # After processing the current source group, leave extra space between networks
    y_source -= 5  # Add a gap between source networks
    y_target -= 2  # Add a gap between target networks

# Make the diagram larger
plt.figure(figsize=(15, 11))  # Adjust the size as needed

# Draw the graph
nx.draw(G, pos, with_labels=True, node_color='lightgreen', edge_color='gray', node_size=2000, font_size=14)

# Extract and format the edge labels (showing weights)
edge_labels = {(row['Source'], row['Target']): f"{str(row['Source']) + '.' + str(row['SPort']) + '   <--->  ' + str(row['Target']) + '.' + str(row['DPort'])}" for index, row in edge_data.iterrows() if pd.notna(row['Target'])}

# Draw the edge labels on the graph
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

# Show the plot and wait for user input
plt.savefig('cdp5_topo4.png')
