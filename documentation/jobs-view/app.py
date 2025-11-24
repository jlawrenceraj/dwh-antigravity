from flask import Flask, jsonify, render_template, abort
import networkx as nx
import os

app = Flask(__name__)

def parse_data(file_path):
    """Parses 'A --> B' format from a file into a NetworkX DiGraph."""
    G = nx.DiGraph()
    if not os.path.exists(file_path):
        return None
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
def index_redirect():
    # Redirect to default app or show a landing page
    return render_template('index.html', app_name='default')

@app.route('/<app_name>')
def index(app_name):
    return render_template('index.html', app_name=app_name)

@app.route('/api/data/<app_name>')
def get_data(app_name):
    file_path = os.path.join('data', app_name, 'jobs.txt')
    G = parse_data(file_path)
    
    if G is None:
        return jsonify({"error": "Application not found"}), 404

    # Find root nodes (nodes with in-degree 0)
    roots = [n for n, d in G.in_degree() if d == 0]
    
    if not roots:
        return jsonify({"name": "No Data", "children": []})

    # Assuming single root for simplicity based on example, but handling multiple just in case
    if len(roots) == 1:
        tree_data = build_hierarchy(G, roots[0])
    else:
        # Create a dummy root if multiple roots exist
        tree_data = {"name": "Root", "children": [build_hierarchy(G, root) for root in roots]}
        
    return jsonify(tree_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
