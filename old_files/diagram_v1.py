import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import csv
import os

# Read the CSV file using pandas
#edge_data = pd.read_csv('C:\Users\phe\Documents\tech\test\shCDP5.csv')
edge_data = pd.read_csv('shCDP5.csv')
print(edge_data)

# Create a new graph
G = nx.Graph()

# Add edges from the CSV file
# Assuming the CSV file has columns 'Source' and 'Target'
for index, row in edge_data.iterrows():
    G.add_edge(row['Source'], row['Target'])
    #print(edge_data(row['Source']))

# Draw the graph
nx.draw(G, with_labels=True, node_color='lightgreen', font_weight='bold', edge_color='gray')

# Display the graph
#plt.show(block=True)
plt.savefig('cdp5_topo.png')
