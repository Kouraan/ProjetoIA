from src.Model.Taxi.Taxi import Taxi
from src.Model.Orders.Order import Order
from src.Model.Charging_Stations.Charge_Station import Charge_Station
from http.server import BaseHTTPRequestHandler
from threading import Lock,Event

class Viewer(BaseHTTPRequestHandler):

    def __init__(self, chargin_stations:list[Charge_Station] = None, taxis:list[Taxi] = None):
        self.last_taxis_report: list[Taxi] = taxis
        self.Orders: list[Order] = list()
        self.charging_Stations: list[Charge_Station] = chargin_stations
        self.l: Lock = Lock()
        self.Running = Event()
        self.Running.set()
    
    def add_Order(self, order:Order):
        with self.l:
            self.Orders.append(order)
    
    def add_Taxi(self, taxi:Taxi):
        with self.l:
            self.last_taxis_report.append(taxi)
    
    def stop(self):
        self.Running.clear()

    
    def json_taxis(self):
        with self.l:
            return [taxi.to_dict() for taxi in self.last_taxis_report]
    
    def json_Orders(self):
        with self.l:    
            return [order.to_dict() for order in self.Orders if not order.isComplete()]
        
    def json_Stations(self):
        with self.l:
            return [station.to_dict() for station in self.charging_Stations]