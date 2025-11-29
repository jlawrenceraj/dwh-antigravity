import pandas as pd
import networkx as nx
from pyvis.network import Network
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import webbrowser

def detect_cycles(G):
    """
    Detects cycles in the directed graph and returns them.
    """
    try:
        cycles = list(nx.simple_cycles(G))
        return cycles
    except:
        return []

def generate_interactive_graph_from_csv(file_path):
    """
    Parses a CSV file with job dependencies and generates an interactive
    network visualization using pyvis. Detects and highlights cyclic dependencies.
    """
    try:
        # Load the CSV data into a pandas DataFrame
        df = pd.read_csv(file_path)

        # Ensure required columns exist
        required_cols = ['JobName', 'Successor']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"CSV must contain columns: {required_cols}")

        # Create a directed graph
        G = nx.DiGraph()

        # Add all unique job names as nodes
        all_jobs = pd.concat([df['JobName'], df['Successor']]).dropna().unique()
        for job in all_jobs:
            G.add_node(job, title=job)

        # Add edges based on JobName -> Successor relationships
        for index, row in df.iterrows():
            job_name = row['JobName']
            successor = row['Successor']

            if pd.notna(job_name) and pd.notna(successor):
                G.add_edge(job_name, successor)

        # Detect cyclic dependencies
        cycles = detect_cycles(G)
        cycle_nodes = set()
        for cycle in cycles:
            cycle_nodes.update(cycle)

        # Use pyvis to create an interactive visualization
        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", directed=True)
        net.from_nx(G)
        
        # Highlight nodes involved in cyclic dependencies
        for node in net.nodes:
            if node['id'] in cycle_nodes:
                node['color'] = '#FF6B6B'  # Red for cyclic dependency nodes
                node['title'] = f"{node['id']} (CYCLIC DEPENDENCY)"
            else:
                node['color'] = '#4ECDC4'  # Teal for normal nodes
        
        # Add basic physics for better layout of large graphs
        net.toggle_physics(True)

        output_path = "ctm_flow_visualization.html"
        net.save_graph(output_path)
        
        cycle_info = f"\n\nCyclic Dependencies Found: {len(cycles)}" if cycles else "\n\nNo Cyclic Dependencies Found"
        if cycles:
            cycle_info += f"\nCycles: {cycles}"
        
        return output_path, G.number_of_nodes(), G.number_of_edges(), cycle_info

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return None, 0, 0, ""

def visualize_ui():
    """
    Tkinter UI to select CSV file and trigger visualization.
    """
    def open_file_dialog_and_visualize():
        file_path = filedialog.askopenfilename(
            title="Select Control-M Flow CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            output_file, nodes_count, edges_count, cycle_info = generate_interactive_graph_from_csv(file_path)
            if output_file:
                messagebox.showinfo("Success", 
                                    f"Parsed {nodes_count} nodes and {edges_count} dependencies.{cycle_info}\n"
                                    f"Interactive graph saved to {os.path.abspath(output_file)}\n"
                                    "Opening in web browser now...")
                
                # Open the generated HTML file in the default web browser
                webbrowser.open('file://' + os.path.abspath(output_file))

    root = tk.Tk()
    root.title("CTM Flow CSV Viewer")
    root.geometry("400x150")

    tk.Label(root, text="Visualize Control-M Job Dependencies from CSV").pack(pady=10)
    
    open_button = tk.Button(root, text="Select CSV File and View Flow", command=open_file_dialog_and_visualize)
    open_button.pack(pady=20)
    
    root.mainloop()

def process_file(file_path):
    """
    Process a CSV file and generate visualization.
    Supports both relative and absolute paths.
    """
    # Convert relative path to absolute if needed
    if not os.path.isabs(file_path):
        file_path = os.path.abspath(file_path)
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False
    
    print(f"Processing file: {file_path}")
    output_file, nodes_count, edges_count, cycle_info = generate_interactive_graph_from_csv(file_path)
    
    if output_file:
        print(f"✓ Parsed {nodes_count} nodes and {edges_count} dependencies.{cycle_info}")
        print(f"✓ Interactive graph saved to {os.path.abspath(output_file)}")
        print(f"✓ Opening in web browser...")
        webbrowser.open('file://' + os.path.abspath(output_file))
        return True
    return False

if __name__ == "__main__":
    # Check if a file path was provided as command-line argument
    if len(sys.argv) > 1:
        # Command-line mode: process the file directly
        csv_file = sys.argv[1]
        process_file(csv_file)
    else:
        # GUI mode: show file dialog
        visualize_ui()

