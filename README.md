# Georgia Tech Course Prerequisites Visualization

Directed acyclic graph visualization of Georgia Tech's prerequisite chains. On hover, nodes also show the course description, exact prerequisites, and past professors and terms taught.

The data is scraped from [OSCAR](https://oscar.gatech.edu/bprod/bwckschd.p_disp_dyn_sched) and GT's [Math website](https://www.math.gatech.edu) into a CSV file. The network is generated using pyvis in `gen_network.py`, which reads the CSV files and generates the HTML file. The HTML file is then slightly modified using `inject.py`.

Edges are drawn by taking the highest required prerequisites for each course. Note that some courses such as MATH 3215 and MATH 3670 have less priority if they are not for math majors.

- [Live Math Visualization](https://echen333.github.io/class_viz/network_math.html)

Also, the CS visualization is not as nice since most graduate classes don't have prerequisites listed.

To compile it locally,

```bash
pip install pandas, networkx, pyvis
python3 gen_network.py && python3 inject.py network_math.html network_math.html 
```
