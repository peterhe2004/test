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
    
# Assign source nodes to the left and target nodes to the right
x_source = -1  # Fixed x-coordinate for source nodes (left side)
x_target = 13   # Fixed x-coordinate for target nodes (right side)
y_source = 0   # Initial y-coordinate for source nodes (incremental)
y_target = 0   # Initial y-coordinate for target nodes (incremental)

for index, row in edge_data.iterrows():
    source = row['Source']
    target = row['Target']
    
    #If source node not already placed, place it on the left
    if source not in pos:
        pos[source] = (x_source, y_source)
        y_source += 1  # Increment the y-position for the next source node
    #If target node not already placed, place it on the right
    if target not in pos:
      pos[target] = (x_target, y_target)
      y_target += 1  # Increment the y-position for the next target node

# Make the diagram larger
plt.figure(figsize=(15, 11))  # Adjust the size as needed

# Draw the graph
nx.draw(G, pos, with_labels=True, node_color='lightgreen', edge_color='gray', node_size=2000, font_size=14)

# Extract and format the edge labels (showing weights)
edge_labels = {(row['Source'], row['Target']): f"{str(row['Source']) + '.' + str(row['SPort']) + '   <--->  ' + str(row['Target']) + '.' + str(row['DPort'])}" for index, row in edge_data.iterrows() if pd.notna(row['Target'])}

# Draw the edge labels on the graph
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

# Show the plot and wait for user input
plt.savefig('cdp5_topo2.png')
