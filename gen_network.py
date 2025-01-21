import pandas as pd
import networkx as nx
from pyvis.network import Network
import ast
import textwrap

def format_text_with_breaks(text, width=100):
    if not pd.notna(text):
        return ""
    
    formatted = "" + str(text) if text else ""
    formatted = formatted.replace('\n', ' ')
    
    # Use textwrap to split at word boundaries
    lines = textwrap.wrap(formatted, width=width, break_long_words=True)
    # lines = textwrap.fill(formatted, width=width).split('\n')
    
    return '<br/>'.join(lines)
  
# Read the data
# df = pd.read_csv('gt_math_courses.csv')
file_path = 'data2/gt_math_courses.csv'
df = pd.read_csv(file_path)
# Filter out special topics courses
df = df[~df['title'].str.contains('Special Topics', case=False, na=False)]
df = df[~df['title'].str.contains('Honors', case=False, na=False)]

file_path2 = 'data2/gt_math_courses_20250121_034050.csv'
df2 = pd.read_csv(file_path2)

less_prio_numbers = []
if file_path.lower().find('math') != -1:
  print("Adding less priority to 3215 and 3670 and 2605")
  less_prio_numbers = ['3215', '3670', '2605','2603']
  print("Removing 2406")
  df = df[~df['title'].str.contains('2406', case=False, na=False)]
  
  
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
    
    # Format description with line breaks using HTML line breaks
    title = f"<h3>{row['title']}</h3><br/>"
    desc = row['description'] 
    formatted_desc = desc.replace('\n', ' ')
    
    # Get prerequisites and format them
    prereqs = ast.literal_eval(row['prerequisites'])
    prereqs_prefix = "<br/><br/><b>Prerequisites:</b> "
    prereq_text = str(row['prereq_text']).replace('\n', ' ') if row['prereq_text'] and not pd.isna(row['prereq_text']) else "None"
    if prereq_text.find("None") != -1:
      # try getting from df2
      df2_row = df2[df2['course_number'] == int(row['number'])]
      if len(df2_row) > 0:
        prereq_text = str(df2_row['prerequisites_text_raw'].values[0]).replace('\n', ' ') if df2_row['prerequisites_text_raw'].values[0] and not pd.isna(df2_row['prerequisites_text_raw'].values[0]) else "None"
    prereq_text = prereqs_prefix + prereq_text
    
    # Clean up professors and terms strings by removing all line breaks and extra whitespace
    prof_and_terms = "<br/><br/><i>Professors:</i> " + ' '.join(str(row['professors_str']).replace('\n', ' ').split()) + "<br/><i>Last taught in:</i> " + ' '.join(str(row['terms_str']).replace('\n', ' ').replace('<br/>', ' ').split())
    
    # Split text into chunks of 80 chars and join with <br/>
    title_with_breaks = format_text_with_breaks(title)
    desc_with_breaks = format_text_with_breaks(formatted_desc)
    prereq_with_breaks = format_text_with_breaks(prereq_text)
    prof_and_terms_with_breaks = format_text_with_breaks(prof_and_terms)
    full_text = f"<div>{title_with_breaks}{desc_with_breaks}{prereq_with_breaks}{prof_and_terms_with_breaks}</div>"
    
    net.add_node(row['number'],
                # title=full_text,  # Show description and prerequisites on hover
                desc=full_text,
                label=row['title'],  # Only show title, not number
                color=color)

def get_prereq_edge(prereqs, course_number, numbers_list):
    """Get highest prerequisite edge for a course.
    
    Args:
        prereqs: List of prerequisites
        course_number: Course number to find prereqs for
        numbers_list: List of valid course numbers
        
    Returns:
        Tuple of (prereq_num, course_number) or None if no valid prereq found
    """
    max_prereq = None
    max_prereq_num = -1
    alternate_prereq = -1
    
    for prereq in prereqs:
        prereq_num = prereq.split(' ')[1]
        # Check if prereq exists in our course list before adding edge
        if prereq_num in numbers_list:  # Ensure prereq exists in our course list
            try:
                prereq_int = int(prereq_num)
                if prereq_int > max_prereq_num and prereq_int < int(course_number) and prereq_int != int(course_number) and str(prereq_int) not in less_prio_numbers:
                    max_prereq_num = prereq_int
                    max_prereq = prereq_num
                elif prereq_int > alternate_prereq and prereq_int != int(course_number):
                    alternate_prereq = prereq_int
            except ValueError:
                continue
        else:
            pass
            
    return max_prereq, alternate_prereq

# Create edges using course numbers - only highest prerequisite
edges = []
for index, row in df.iterrows():
    # First try must-have prerequisites
    prereqs = ast.literal_eval(row['must_have_prereqs'])
    max_prereq, alternate_prereq = get_prereq_edge(prereqs, row['number'], numbers_list)
    
    print(row['number'], row['must_have_prereqs'], row['optional_prereqs'])
    if max_prereq:
        edges.append((max_prereq, row['number']))
        continue
    elif alternate_prereq != -1 and str(alternate_prereq) in numbers_list:
        edges.append((str(alternate_prereq), row['number']))
        continue
        
    # If no must-have prereqs found, try optional prerequisites
    prereqs = ast.literal_eval(row['optional_prereqs']) 
    max_prereq, alternate_prereq = get_prereq_edge(prereqs, row['number'], numbers_list)
    if max_prereq:
        edges.append((max_prereq, row['number']))
        continue
    elif alternate_prereq != -1 and str(alternate_prereq) in numbers_list:
        edges.append((str(alternate_prereq), row['number']))
        continue
    
    # take edges from df2
    if file_path.lower().find('math') != -1:
      df2_row = df2[df2['course_number'] == int(row['number'])]
      print(row['number'], df2_row['must_have_prerequisites_array'], df2_row['optional_prerequisites_array'])
      if len(df2_row) > 0:
        prereqs = ast.literal_eval(df2_row['must_have_prerequisites_array'].values[0])
        max_prereq, alternate_prereq = get_prereq_edge(prereqs, row['number'], numbers_list)
        print("GOT",prereqs, row['number'], max_prereq, alternate_prereq)
        if max_prereq:
          edges.append((max_prereq, row['number']))
          continue
        elif alternate_prereq != -1 and str(alternate_prereq) in numbers_list:
          edges.append((str(alternate_prereq), row['number']))
          continue
        else:
          prereqs = ast.literal_eval(df2_row['optional_prerequisites_array'].values[0])
          max_prereq, alternate_prereq = get_prereq_edge(prereqs, row['number'], numbers_list)
          print("GOT OPTIONAL",prereqs, row['number'], max_prereq, alternate_prereq)
          if max_prereq:
            edges.append((max_prereq, row['number']))
            continue
          elif alternate_prereq != -1 and str(alternate_prereq) in numbers_list:
            edges.append((str(alternate_prereq), row['number']))
            continue

print("Edges:", edges)
print("\nAll course numbers:", sorted(numbers_list))

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