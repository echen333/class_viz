# Class Viz

Visualization of GT's prerequisite chains. Basically, for every class, we draw a directed edge from its highest prerequisite in the same department. 

- [Live Math Visualization](https://echen333.github.io/class_viz/network_math.html)
- [Live CS Visualization](https://echen333.github.io/class_viz/network_cs.html)

## Requirements

- Python 3.10+

```bash
pip install pandas, networkx, pyvis
python3 network_gen.py && python3 inject.py network_math.html network_math.html
```