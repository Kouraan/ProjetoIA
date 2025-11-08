import googlemaps
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
gmaps = googlemaps.Client(key=API_KEY)

# Função para obter o tempo de transito em tempo real quando é feito um pedido
def tempo_com_trafego(origem, destino):
    result = gmaps.distance_matrix(
        origem,
        destino,
        mode="driving",
        region="pt",
        departure_time="now"
    )
    info = result["rows"][0]["elements"][0]
    if info["status"] == "OK":
        tempo = info.get("duration_in_traffic", info["duration"])
        return round((tempo["value"] / 60.0), 2)
    return None