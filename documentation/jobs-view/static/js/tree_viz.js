// Set dimensions
const margin = { top: 20, right: 90, bottom: 30, left: 90 };
const width = window.innerWidth;
const height = window.innerHeight - 100; // Adjust for header

// Create SVG container
const svg = d3.select("#tree-container").append("svg")
    .attr("width", width)
    .attr("height", height)
    .call(d3.zoom().on("zoom", (event) => {
        g.attr("transform", event.transform);
    }))
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

const g = svg.append("g");

// Define arrow marker
svg.append("defs").append("marker")
    .attr("id", "arrow")
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 9) // Adjusted for larger marker
    .attr("refY", 0)
    .attr("markerWidth", 8) // Larger arrow
    .attr("markerHeight", 8)
    .attr("orient", "auto")
    .append("path")
    .attr("d", "M0,-5L10,0L0,5")
    .attr("fill", "#64748b"); // Darker slate color

let i = 0,
    duration = 750,
    root;

// Declares a tree layout and assigns the size
// Increased nodeSize width to accommodate wider boxes
const treeMap = d3.tree().nodeSize([220, 120]);

// Fetch data
fetch('/api/data')
    .then(response => response.json())
    .then(data => {
        root = d3.hierarchy(data, function (d) { return d.children; });
        root.x0 = width / 2;
        root.y0 = 0;

        update(root);
    });

function update(source) {

    // Assigns the x and y position for the nodes
    const treeData = treeMap(root);

    // Compute the new tree layout.
    const nodes = treeData.descendants(),
        links = treeData.descendants().slice(1);

    // Normalize for fixed-depth.
    nodes.forEach(function (d) { d.y = d.depth * 120 }); // Vertical spacing

    // ****************** Nodes section ***************************

    // Update the nodes...
    const node = g.selectAll('g.node')
        .data(nodes, function (d) { return d.id || (d.id = ++i); });

    // Enter any new modes at the parent's previous position.
    const nodeEnter = node.enter().append('g')
        .attr('class', 'node')
        .attr("transform", function (d) {
            return "translate(" + source.x0 + "," + source.y0 + ")";
        })
        .on('click', click);

    // Add Rect for the nodes
    nodeEnter.append('rect')
        .attr('class', 'node')
        .attr('width', 1e-6) // Start small for transition
        .attr('height', 1e-6)
        .attr('x', 0)
        .attr('y', 0)
        .style("fill", function (d) {
            return d._children ? "#0ea5e9" : "#ffffff";
        });

    // Add labels for the nodes
    nodeEnter.append('text')
        .attr("dy", ".35em")
        .attr("text-anchor", "middle")
        .text(function (d) { return d.data.name; })
        .each(function (d) {
            // Calculate width based on text length
            d.width = this.getComputedTextLength() + 20; // Padding
            d.height = 30; // Fixed height
        });

    // UPDATE
    const nodeUpdate = nodeEnter.merge(node);

    // Transition to the proper position for the node
    nodeUpdate.transition()
        .duration(duration)
        .attr("transform", function (d) {
            return "translate(" + d.x + "," + d.y + ")";
        });

    // Update the node attributes and style
    nodeUpdate.select('rect.node')
        .attr('width', function (d) { return d.width; })
        .attr('height', function (d) { return d.height; })
        .attr('x', function (d) { return -d.width / 2; }) // Center horizontally
        .attr('y', function (d) { return -d.height / 2; }) // Center vertically
        .style("fill", function (d) {
            return d._children ? "#0ea5e9" : "#ffffff";
        })
        .attr('cursor', 'pointer');

    // Ensure text is centered
    nodeUpdate.select('text')
        .style('fill-opacity', 1);


    // Remove any exiting nodes
    const nodeExit = node.exit().transition()
        .duration(duration)
        .attr("transform", function (d) {
            return "translate(" + source.x + "," + source.y + ")";
        })
        .remove();

    nodeExit.select('rect')
        .attr('width', 1e-6)
        .attr('height', 1e-6);

    nodeExit.select('text')
        .style('fill-opacity', 1e-6);

    // ****************** Links section ***************************

    // Update the links...
    const link = g.selectAll('path.link')
        .data(links, function (d) { return d.id; });

    // Enter any new links at the parent's previous position.
    const linkEnter = link.enter().insert('path', "g")
        .attr("class", "link")
        .attr("marker-end", "url(#arrow)")
        .attr('d', function (d) {
            const o = { x: source.x0, y: source.y0 }
            return diagonal(o, o)
        });

    // UPDATE
    const linkUpdate = linkEnter.merge(link);

    // Transition back to the parent element position
    linkUpdate.transition()
        .duration(duration)
        .attr('d', function (d) { return diagonal(d.parent, d) });

    // Remove any exiting links
    const linkExit = link.exit().transition()
        .duration(duration)
        .attr('d', function (d) {
            const o = { x: source.x, y: source.y }
            return diagonal(o, o)
        })
        .remove();

    // Store the old positions for transition.
    nodes.forEach(function (d) {
        d.x0 = d.x;
        d.y0 = d.y;
    });

    // Creates a curved (diagonal) path from parent to the child nodes
    function diagonal(s, d) {
        // Vertical layout
        const sx = s.x;
        const sy = s.y + 15; // Bottom of source (height/2)
        const dx = d.x;
        const dy = d.y - 15 - 8; // Top of target (height/2 + arrow padding)

        const path = `M ${sx} ${sy}
                C ${sx} ${(sy + dy) / 2},
                  ${dx} ${(sy + dy) / 2},
                  ${dx} ${dy}`

        return path
    }

    // Toggle children on click.
    function click(event, d) {
        if (d.children) {
            d._children = d.children;
            d.children = null;
        } else {
            d.children = d._children;
            d._children = null;
        }
        update(d);
    }
}
