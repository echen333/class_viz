#!/usr/bin/env python3

import sys

def main():
    if len(sys.argv) < 3:
        print("Usage: python inject.py <input.html> <output.html>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 1) Update options to add interaction settings
    #    Adjust the old-string match as needed to match what's in your file.
    old_options = (
        'var options = {"physics": {"forceAtlas2Based": {"gravitationalConstant": -100, '
        '"springLength": 200}, "minVelocity": 0.75, "solver": "forceAtlas2Based"}, '
        '"nodes": {"font": {"size": 14}}};'
    )
    new_options = (
        'var options = {"physics": {"forceAtlas2Based": {"gravitationalConstant": -100, '
        '"springLength": 200}, "minVelocity": 0.75, "solver": "forceAtlas2Based"}, '
        '"nodes": {"font": {"size": 14}}, "interaction": {"hover": true, "tooltipDelay": 50}};'
    )
    content = content.replace(old_options, new_options)

    # 2) Snippet to insert after "drawGraph();"
    #    This snippet assumes 'data' and 'network' become accessible after drawGraph() returns.
    tooltip_snippet = r"""
var network = drawGraph();

// Get nodes reference from data
var nodes = data.nodes;

// Create tooltip element if it doesn't exist
var tooltip = document.createElement('div');
tooltip.id = 'customTooltip';
tooltip.style.position = 'absolute';
tooltip.style.display = 'none';
tooltip.style.pointerEvents = 'none';
tooltip.style.padding = '6px';
tooltip.style.border = '1px solid #ccc';
tooltip.style.borderRadius = '4px';
tooltip.style.backgroundColor = '#f8f8f8';
tooltip.style.fontFamily = 'sans-serif';
tooltip.style.fontSize = '14px';
tooltip.style.zIndex = '99999';
document.body.appendChild(tooltip);

network.on("hoverNode", function (params) {
    var nodeId = params.node;
    if (!nodeId) return;

    var nodeData = nodes.get(nodeId);
    if (!nodeData || !nodeData.desc) {
        tooltip.style.display = 'none';
        return;
    }

    tooltip.innerHTML = nodeData.desc;
    tooltip.style.display = 'block';

    // Position tooltip near cursor
    var canvasPosition = network.getPosition(nodeId);
    var DOMPosition = network.canvasToDOM(canvasPosition);
    tooltip.style.left = (DOMPosition.x + 15) + 'px';
    tooltip.style.top = (DOMPosition.y + 15) + 'px';
});

network.on("blurNode", function (params) {
    tooltip.style.display = 'none';
});
"""

    # 3) Replace the line 'drawGraph();' with the snippet above
    #    Or insert right after it. Here we replace the occurrence directly.
    content = content.replace(
        'drawGraph();',
        tooltip_snippet
    )

    # 4) Write out the updated file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
