from enum import Enum
from src.Model.Graph.Node import Node

class Order_Status(Enum):
    Pendent = 1,
    In_Progress = 2,
    Concluded = 3,
    Rejected = 4

class Order:
    def __init__(self,id, source:int, destination:int, passengers, schedule, priority, prefAmbiental=None, tempo_espera=None):
        self.id = id
        self.source = source
        self.destination = destination
        self.passengers = passengers
        self.schedule = schedule              
        self.priority = priority
        self.prefAmbiental = prefAmbiental
        self.status = Order_Status.Pendent           
        self.vehicle_id = None
        self.response_time = None

    def get_destination(self):
        return self.destination
    
    def get_source(self):
        return self.source
    
    