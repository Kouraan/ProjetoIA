from random import randint
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
    G = ox.routing.add_edge_speeds(G)
    G = ox.routing.add_edge_travel_times(G)
    for u, v, data in G.edges(data=True):
        totalCapacity = calculate_capacity(data)
        random_capacity = randint(int(0.5 * totalCapacity), totalCapacity)
        current_capacity = round(random_capacity/totalCapacity, 4)
        edges.append({
            "from": u,
            "to": v,
            "length": round(data.get("length", 0), 2), # metros
            "occupancy": current_capacity, # entre 0 e 1
            "travel_time": round(data.get("travel_time", 0) * (current_capacity + 1), 2) #segundos
        })
        
    data = {
        "nodes": nodes,
        "edges": edges
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/braga_map.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Mapa das ruas de Braga criado com sucesso em 'data/braga_map.json'")

def calculate_capacity(edge):
    try:
        lanes = int(str(edge['lanes']).strip("[]").split(',')[0])
    except (KeyError, ValueError):
        lanes = 1
    
    if lanes == 0:
        lanes = 1

    road_type = edge.get("highway", "residential")
    if road_type in ["motorway", "trunk"]:
        capacity_per_lane = 2000
    elif road_type in ["primary", "secondary"]:
        capacity_per_lane = 1400
    else:
        capacity_per_lane = 800
    return lanes * capacity_per_lane

if __name__ == "__main__":
    build_map()