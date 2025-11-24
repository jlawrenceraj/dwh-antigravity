from flask import Flask, jsonify, render_template
import networkx as nx

app = Flask(__name__)

def parse_data(file_path):
    """Parses 'A --> B' format from a file into a NetworkX DiGraph."""
    G = nx.DiGraph()
    with open(file_path, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if '-->' in line:
            parent, child = line.split('-->')
            G.add_edge(parent.strip(), child.strip())
    return G

def build_hierarchy(G, node):
    """Recursively builds a hierarchy dictionary for D3.js."""
    children = [build_hierarchy(G, child) for child in G.successors(node)]
    if children:
        return {"name": node, "children": children}
    else:
        return {"name": node}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    G = parse_data('jobs.txt')
    # Find root nodes (nodes with in-degree 0)
    roots = [n for n, d in G.in_degree() if d == 0]
    
    # Assuming single root for simplicity based on example, but handling multiple just in case
    if len(roots) == 1:
        tree_data = build_hierarchy(G, roots[0])
    else:
        # Create a dummy root if multiple roots exist
        tree_data = {"name": "Root", "children": [build_hierarchy(G, root) for root in roots]}
        
    return jsonify(tree_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
