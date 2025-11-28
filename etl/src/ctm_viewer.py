pip install networkx matplotlib


import xml.etree.ElementTree as ET
import networkx as nx
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog, Button, Label, messagebox, simpledialog

def parse_ctm_xml(xml_file_path):
    """
    Parses a Control-M job definition XML file and extracts jobs and dependencies.
    Returns a directed graph (DiGraph) using NetworkX.
    """
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    G = nx.DiGraph()
    jobs = {} # Dictionary to quickly look up job names/IDs

    # Helper function to extract job information recursively from folders/subfolders
    def extract_jobs_recursive(parent_element, parent_name=None):
        for job_elem in parent_element.findall('JOB'):
            job_name = job_elem.get('JOBNAME')
            jobs[job_name] = job_elem
            G.add_node(job_name, type='Job', parent=parent_name)
            if parent_name:
                # Add implicit parent-child link if it helps visualization
                pass 

        for folder_elem in parent_element.findall('FOLDER'):
            folder_name = folder_elem.get('FOLDER_NAME')
            G.add_node(folder_name, type='Folder', parent=parent_name)
            extract_jobs_recursive(folder_elem, folder_name)

    # Start extraction from the root FOLDER or JOBS element
    # Adjust tag names based on your specific CTM XML version/structure
    top_folder = root.find('FOLDER') or root.find('.') # Assuming top-level is a FOLDER or JOBS tag
    if top_folder is not None:
        extract_jobs_recursive(top_folder)
    else:
        # Handle case where jobs might be directly under root (less common for large flows)
        extract_jobs_recursive(root)

    # Process dependencies (In/Out conditions are standard CTM dependencies)
    for job_name, job_elem in jobs.items():
        in_conditions = job_elem.findall('.//INCOND')
        for cond in in_conditions:
            # Note: CTM conditions are tricky as the "from" job might be in another folder
            # This simplified approach assumes the 'from' job name exists in our graph nodes
            from_job = cond.get('PRE_REQ_JOB_NAME')
            if from_job in G.nodes:
                # Edge goes from the source job (from_job) to the current job (job_name)
                G.add_edge(from_job, job_name, condition=cond.get('COND_NAME'))

    return G

def visualize_graph_ui():
    """
    Tkinter UI to select XML file and trigger visualization.
    """
    def open_file_dialog_and_visualize():
        file_path = filedialog.askopenfilename(
            title="Select Control-M XML File",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if file_path:
            try:
                graph = parse_ctm_xml(file_path)
                num_nodes = graph.number_of_nodes()
                num_edges = graph.number_of_edges()

                if num_nodes > 1000:
                    messagebox.showinfo("Large Graph Info", 
                                        f"Parsed {num_nodes} nodes and {num_edges} dependencies.\n"
                                        "Visualization might take a moment or be cluttered due to scale.")
                
                # --- Visualization using Matplotlib and NetworkX ---
                plt.figure(figsize=(12, 12))
                
                # Use a layout that handles hierarchical/tree structures well
                # 'dot' layout from graphviz provides a good hierarchical view, but needs pygraphviz
                # Fallback to spring layout (might be messy for 1000 nodes)
                try:
                    # Requires `pip install pygraphviz` and graphviz system libraries
                    pos = nx.nx_agraph.graphviz_layout(graph, prog='dot')
                except ImportError:
                    pos = nx.spring_layout(graph, k=0.3, iterations=50) # Fallback layout

                nx.draw(graph, pos, with_labels=True, node_size=50, node_color='lightblue', font_size=6, arrows=True)
                plt.title(f"Control-M Flow Visualization ({num_nodes} jobs)")
                plt.show()

            except ET.ParseError as e:
                messagebox.showerror("XML Error", f"Failed to parse XML file: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    root = Tk()
    root.title("CTM XML Flow Viewer")
    root.geometry("350x150")

    Label(root, text="Visualize Control-M Job Definitions from XML").pack(pady=10)
    
    open_button = Button(root, text="Select XML File and View Flow", command=open_file_dialog_and_visualize)
    open_button.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    visualize_graph_ui()
