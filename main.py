import numpy as np
from src.Model.Taxi.Taxi import Taxi
import osmnx as ox
from src.Model.Graph.Graph import Graph
from src.Model.Orders.OrderManager import OrderManager
from src.View.Viewer import Viewer  
from src.TaxiGreen import TaxiGreen
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

default_number_of_taxis = 5
default_search_algorithm = 2

taxi_green = TaxiGreen(default_number_of_taxis, default_search_algorithm, 0.5)



@app.route("/")
def simulation_view():
    return render_template("map.html")


@app.route("/taxis")
def get_taxis():
    return taxi_green.viewer.json_taxis()
    

@app.route("/orders")
def get_orders():
    return taxi_green.viewer.json_Orders()


@app.route("/start",methods=["POST"])
def start():
    global taxi_green
    parameter = request.json or {}
    number_of_taxis = parameter.get("number_of_taxis", 5)
    search_algorithm = parameter.get("search_algorithm", 2)
    taxi_green.stop()
    taxi_green = TaxiGreen(number_of_taxis, search_algorithm, 0.5)
    taxi_green.start_simulation()
    return jsonify({
        "status": "started",
        "number_of_taxis": number_of_taxis,
        "search_algorithm": search_algorithm
    })


@app.route("/stop",methods=["POST"])
def stop():
    taxi_green.stop()

@app.route("/reset", methods=["POST"])
def reset():
    global taxi_green
    parameter = request.json or {}
    
    taxi_green.stop()
    
    number_of_taxis = parameter.get("number_of_taxis", 5)
    
    taxi_green = TaxiGreen(number_of_taxis) 
    taxi_green.start_simulation()
    
    return jsonify({"status": "reset", "number_of_taxis": number_of_taxis})



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)