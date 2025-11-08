import googlemaps
import json
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
gmaps = googlemaps.Client(key=API_KEY)

#Locais de Braga
LOCATIONS = [
    "Universidade do Minho, Braga",
    "Braga Parque, Braga",
    "Sé de Braga",
    "Estação de Comboios de Braga",
    "Altice Forum Braga",
    "Bom Jesus do Monte",
    "Largo Senhora-a-Branca, Braga",
    "Monte do Picoto, Braga"
]

# Constroi o mapa de Braga com distâncias e tempos entre os locais
def build_map():
    edges = []
    # Criar todas as ligações entre os locais
    for i, origin in enumerate(LOCATIONS):
        for j, destination in enumerate(LOCATIONS):
            if i < j:
                result = gmaps.distance_matrix(
                    origin,
                    destination,
                    mode="driving",
                    region="pt",
                    departure_time="now"  # Para obter duração com trânsito
                )
                info = result["rows"][0]["elements"][0]
                if info["status"] == "OK":
                    distance_km = info["distance"]["value"] / 1000.0 # converter metros para km
                    time_min = info["duration"]["value"] / 60.0 # converter segundos para minutos
                    edges.append({
                        "from": origin,
                        "to": destination,
                        "distance": round(distance_km, 2),
                        "time": round(time_min, 2),
                    })
    # Estrutura do grafo
    data = {
        "nodes": LOCATIONS,
        "edges": edges
    }
    
    # Garantir que a pasta 'data' existe
    os.makedirs("data", exist_ok=True)
    
    # Guardar em JSON
    with open("data/map.json", "w", encoding= "utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print("Mapa de Braga criado com sucesso em 'data/map.json'.")
    
if __name__ == "__main__":
    build_map()