#from flask import Flask, jsonify, send_from_directory, Response
import numpy as np
from src.Model.Taxi.Taxi import Taxi
import osmnx as ox
from src.Model.Graph.Graph import Graph
from src.Model.Orders.OrderManager import OrderManager 
from src.TaxiGreen import TaxiGreen

app = TaxiGreen(5)
app.start_simulation()



