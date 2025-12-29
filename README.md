# TaxiGreen — Braga demo

This small demo uses Flask to serve a Leaflet map and OSMnx to download the road network for Braga, Portugal. The Flask backend exposes a GeoJSON endpoint (`/graph.geojson`) that the browser fetches and draws with Leaflet.

Quick start

1. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

Note: `osmnx` has additional system dependencies (GDAL, GEOS). On macOS you can often install those via `brew install gdal geos proj`. If installation issues occur, see OSMnx installation docs.

3. Run the app:

```bash
python main.py
```

4. Open http://127.0.0.1:5000/ in your browser. The server will start a background thread to download the Braga graph; the page will retry until the GeoJSON is ready.

Files

- `main.py` — Flask app that builds the OSMnx graph and serves `/graph.geojson`.
- `map.html` — Leaflet client that fetches and renders the graph.
- `requirements.txt` — Python dependencies.

If you want to adapt the place, change the `graph_from_place` call in `main.py`.
