Predecessor,JobName,Successor
Start_Node,Job_A,Job_B
Job_A,Job_B,Job_C
Job_B,Job_C,Job_D
Job_C,Job_D,End_Node
Start_Node,Job_E,Job_F
Job_E,Job_F,Job_D
,,,Job_G
Job_G,,,

python ctm_csv_viewer.py



import pandas as pd
import networkx as nx
from pyvis.network import Network
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def generate_interactive_graph_from_csv(file_path):
    """
    Parses a CSV file with job dependencies and generates an interactive
    network visualization using pyvis.
    """
    try:
        # Load the CSV data into a pandas DataFrame
        df = pd.read_csv(file_path)

        # Ensure required columns exist (adjust names if necessary)
        required_cols = ['Predecessor', 'JobName', 'Successor']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"CSV must contain columns: {required_cols}")

        # Create a directed graph
        G = nx.DiGraph()

        # Add all unique job names as nodes
        all_jobs = pd.concat([df['Predecessor'], df['JobName'], df['Successor']]).dropna().unique()
        for job in all_jobs:
            G.add_node(job, title=job) # title attribute used for tooltips

        # Add edges based on predecessor -> JobName and JobName -> Successor relationships
        for index, row in df.iterrows():
            predecessor = row['Predecessor']
            job_name = row['JobName']
            successor = row['Successor']

            if pd.notna(predecessor) and pd.notna(job_name):
                G.add_edge(predecessor, job_name)
            if pd.notna(job_name) and pd.notna(successor):
                G.add_edge(job_name, successor)
            # Handle stand-alone jobs (JobName only row) - they should already be nodes

        # Use pyvis to create an interactive visualization
        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", directed=True)
        net.from_networkx(G)
        
        # Add basic physics for better layout of large graphs
        net.toggle_physics(True)

        output_path = "ctm_flow_visualization.html"
        net.save_fig(output_path)
        
        return output_path, G.number_of_nodes(), G.number_of_edges()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return None, 0, 0

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
            output_file, nodes_count, edges_count = generate_interactive_graph_from_csv(file_path)
            if output_file:
                messagebox.showinfo("Success", 
                                    f"Parsed {nodes_count} nodes and {edges_count} dependencies.\n"
                                    f"Interactive graph saved to {os.path.abspath(output_file)}\n"
                                    "Opening in web browser now...")
                
                # Open the generated HTML file in the default web browser
                import webbrowser
                webbrowser.open('file://' + os.path.abspath(output_file))

    root = Tk()
    root.title("CTM Flow CSV Viewer")
    root.geometry("400x150")

    Label(root, text="Visualize Control-M Job Dependencies from CSV").pack(pady=10)
    
    open_button = Button(root, text="Select CSV File and View Flow", command=open_file_dialog_and_visualize)
    open_button.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    visualize_ui()

