import pandas as pd
import networkx as nx
from pyvis.network import Network
import ast

# Read the data
# df = pd.read_csv('gt_math_courses.csv')
df = pd.read_csv('gt_math_courses.csv')
# Filter out special topics courses
df = df[~df['title'].str.contains('Special Topics', case=False, na=False)]

# Extract course numbers and create a mapping of numbers to full titles
df['number'] = df['title'].str.extract(r'(\d+)')
title_mapping = df.set_index('number')['title'].to_dict()
numbers_list = df['number'].unique()

# Define color mapping based on first digit
color_map = {
    '0': '#FFD700', # gold
    '1': '#FFB6C1',  # Light pink
    '2': '#98FB98',  # Pale green
    '3': '#87CEFA',  # Light sky blue
    '4': '#DDA0DD',  # Plum
    '6': '#F0E68C',  # Khaki
    '7': '#FFA07A',  # Light salmon
    # light yellow
    '8': '#FFFFE0',
}

df['class_name'] = df['title'].str.split('-').str[1]

# Create directed graph
net = nx.DiGraph()

# Add nodes with only title as label, colored by first digit
for index, row in df.iterrows():
    first_digit = row['number'][0] if row['number'] else None
    color = color_map.get(first_digit, '#CCCCCC')  # Default gray if no matching first digit
    
    net.add_node(row['number'],
                # title=row['class_name'],  # This will show on hover
                label=row['title'],  # Only show title, not number
                color=color)

# Create edges using course numbers - only highest prerequisite
edges = []
for index, row in df.iterrows():
    prereqs = ast.literal_eval(row['prerequisites'])
    max_prereq = None
    max_prereq_num = -1
    alternate_prereq = -1
    
    for prereq in prereqs:
        prereq_num = prereq.split(' ')[1]
        if (prereq_num in numbers_list and  # Ensure prereq exists in our course list
            row['number'] != prereq_num):   # Avoid self-loops
            try:
                prereq_int = int(prereq_num)
                if prereq_int > max_prereq_num and prereq_int < int(row['number']):
                    max_prereq_num = prereq_int
                    max_prereq = prereq_num
                elif prereq_int > alternate_prereq:
                    alternate_prereq = prereq_int
            except ValueError:
                continue
    
    if max_prereq:
        edges.append((max_prereq, row['number']))
    elif alternate_prereq != -1:
        edges.append((alternate_prereq, row['number']))

# Add edges to graph
net.add_edges_from(edges)

# Create Pyvis network with full screen dimensions
nt = Network(height="100vh",  # Changed to viewport height
            width="100vw",    # Changed to viewport width
            bgcolor="#ffffff",
            directed=True)

# Configure physics options for better spacing
nt.set_options("""
{
  "physics": {
    "forceAtlas2Based": {
      "gravitationalConstant": -100,
      "springLength": 200
    },
    "minVelocity": 0.75,
    "solver": "forceAtlas2Based"
  },
  "nodes": {
    "font": {
      "size": 14
    }
  }
}
""")

# Convert NetworkX graph to Pyvis
nt.from_nx(net)

# Save the interactive visualization
nt.save_graph('network_math.html')