import networkx as nx
from pathlib import Path

def build_graph(parsed_files: list) -> nx.DiGraph:
    """
    Build a directed dependency graph from parsed file data.
    Nodes = files. Edges = import relationships between files.
    """
    G = nx.DiGraph()

    # Map stem names to full paths for import resolution
    stem_map = {Path(p["file"]).stem: p["file"] for p in parsed_files}

    for pf in parsed_files:
        G.add_node(
            pf["file"],
            language=pf.get("language", ""),
            functions=[f["name"] for f in pf.get("functions", [])],
            classes=[c["name"] for c in pf.get("classes", [])],
            num_functions=len(pf.get("functions", [])),
            num_classes=len(pf.get("classes", [])),
        )

    for pf in parsed_files:
        for imp in pf.get("imports", []):
            for stem, full_path in stem_map.items():
                if stem in imp and full_path != pf["file"]:
                    G.add_edge(pf["file"], full_path, label=imp)

    return G

def graph_summary(G: nx.DiGraph) -> dict:
    """Return a high-level summary of the dependency graph."""
    return {
        "total_files": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "hub_files": sorted(
            G.nodes, key=lambda n: G.in_degree(n), reverse=True
        )[:5],
        "isolated_files": [n for n in G.nodes if G.degree(n) == 0],
        "edges": list(G.edges()),
    }

def graph_to_json(G: nx.DiGraph) -> dict:
    """Serialize graph to a JSON-friendly format for the frontend."""
    return {
        "nodes": [
            {
                "id": n,
                "language": G.nodes[n].get("language"),
                "functions": G.nodes[n].get("functions", []),
                "classes": G.nodes[n].get("classes", []),
                "num_functions": G.nodes[n].get("num_functions", 0),
                "num_classes": G.nodes[n].get("num_classes", 0),
                "in_degree": G.in_degree(n),
                "out_degree": G.out_degree(n),
            }
            for n in G.nodes
        ],
        "edges": [
            {"source": u, "target": v, "label": G.edges[u, v].get("label", "")}
            for u, v in G.edges
        ],
    }