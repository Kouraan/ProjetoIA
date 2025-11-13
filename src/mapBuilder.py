import osmnx as ox
import json
import os

def build_map():
    filepath = "data/braga_map.json"
    if os.path.exists(filepath):
        print(f"O ficheiro '{filepath}' já existe. A geração do mapa foi ignorada.")
        return
    
    # Extrair o grafo das ruas de Braga
    G = ox.graph_from_place("Braga, Portugal", network_type="drive")
    
    nodes = []
    for node, data in G.nodes(data=True):
        nodes.append({
            "id": node,
            "x": data.get("x"),
            "y": data.get("y")
        })
        
    edges = []
    for u, v, data in G.edges(data=True):
        edges.append({
            "from": u,
            "to": v,
            "length": round(data.get("length", 0), 2), # metros
        })
        
    data = {
        "nodes": nodes,
        "edges": edges
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/braga_map.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Mapa das ruas de Braga criado com sucesso em 'data/braga_map.json'")
    
if __name__ == "__main__":
    build_map()