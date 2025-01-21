# Class Viz

Visualization of GT's prerequisite chains. Basically, for every class, we draw a directed edge from its highest prerequisite in the same department.

Note: This simplified view can be misleading in cases where multiple different courses could satisfy a single prerequisite requirement.

- [Live Math Visualization](https://echen333.github.io/class_viz/network_math.html)
- [Live CS Visualization](https://echen333.github.io/class_viz/network_cs.html)

The network is generated using pyvis in `gen_network.py`, which reads the CSV files and generates the HTML file. The HTML file is then injected with some data in `inject.py`.

## Requirements

- Python 3.10+

```bash
pip install pandas, networkx, pyvis
python3 gen_network.py && python3 inject.py network_math.html network_math.html 
```
