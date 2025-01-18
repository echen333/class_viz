import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import ast
from pyvis.network import Network

# Read the data
df = pd.read_csv('gt_math_courses.csv')

# Extract course numbers
df['number'] = df['title'].str.extract(r'(\d+)')
numbers_list = df['number'].unique()

# Create directed graph
net = nx.DiGraph()

# Add nodes
for index, row in df.iterrows():
    net.add_node(row['number'], title=row['title'])

# Create edges
edges = []
for index, row in df.iterrows():
    mx = 0
    for prereq in ast.literal_eval(row['prerequisites']):
        if row['number'] != prereq.split(' ')[1] and int(prereq.split(' ')[1]) > mx and prereq.split(' ')[1] in numbers_list:
            mx = int(prereq.split(' ')[1])
    if mx > 0:
        edges.append((mx, row['number']))

# Add edges
net.add_edges_from(edges)

print(net.edges())

# Create a Pyvis network with explicit height and width
nt = Network(height="750px", width="100%", notebook=False, directed=True, bgcolor="#ffffff")
nt.from_nx(net)

# Add some visualization options
nt.toggle_physics(True)
nt.show_buttons(filter_=['physics'])

# Generate the HTML file
nt.save_graph('course_prerequisites.html')  # Using save_graph instead of show

# Optional: Still show matplotlib visualization
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(net)
nx.draw(net, pos, 
        with_labels=True,
        node_color='lightblue',
        node_size=500,
        arrowsize=20,
        arrows=True)
plt.show()