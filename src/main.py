from mapBuilder import build_map
from models import Mapa
from utils import tempo_com_trafego

def main():
    build_map()
    
if __name__ == "__main__":
    main()
    
mapa = Mapa("data/map.json")
print("NOS:")
print(mapa.graph.nodes())

print("\nLIGACOES:")
for u,v, data in mapa.graph.edges(data=True):
    print(f"{u} <-> {v}: {data['distance']} km, {data['time']} min")
    
# ...existing code...

# Testar get_neighbors
print("\nVizinhos do primeiro nó:")
primeiro_no = list(mapa.graph.nodes())[0]
print(mapa.get_neighbors(primeiro_no))

# Testar distance, time e time_with_traffic entre dois nós
no_a = list(mapa.graph.nodes())[0]
no_b = list(mapa.graph.nodes())[1]
print(f"\nDistância entre '{no_a}' e '{no_b}': {mapa.distance(no_a, no_b)} km")
print(f"Tempo normal entre '{no_a}' e '{no_b}': {mapa.time(no_a, no_b)} min")
print(f"Tempo com trânsito entre '{no_a}' e '{no_b}': {tempo_com_trafego(no_a, no_b)} min")