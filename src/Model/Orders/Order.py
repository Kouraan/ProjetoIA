from enum import Enum
from src.Model.Graph.Node import Node
from threading import Lock
from src.Util.coordinates_util import to_latlon
from src.Model.Timer.Clock import Clock


class Order_Status(Enum):
    Pendent = 1,
    In_Progress = 2,
    Concluded = 3,
    Rejected = 4

class Order:
    def __init__(self,id, crs,source:int, destination:int, passengers, schedule, priority:int, prefAmbiental=None, tempo_espera=None,position:tuple[float,float] = (0,0)):
        self.id = id
        self.source = source
        self.lan , self.lot = to_latlon(crs,position[0],position[1])
        self.destination = destination
        self.passengers = passengers
        self.schedule = schedule              
        self.priority = priority
        self.prefAmbiental = prefAmbiental
        self.status = Order_Status.Pendent.value           
        self.vehicle_id = None
        self.response_time = None
        self.completion_time = 0
        self.l = Lock()

    def get_destination(self):
        with self.l:
            return self.destination
    
    def get_source(self):
        with self.l:
            return self.source
    

    def get_passengers(self):
        with self.l:
            return self.passengers


    def to_dict(self):
        with self.l:
            return {
                "id": self.id,
                "source": self.source,
                "destination": self.destination,
                "position": [self.lan,self.lot],
                "passengers": self.passengers,
                "schedule": self.schedule,
                "priority": self.priority,
                "prefAmbiental": self.prefAmbiental,
                "status": Order_Status(self.status).name,
                "vehicle_id": self.vehicle_id,
                "response_time": self.response_time
            }
    
    def complete(self, clock:Clock):
        with self.l:
            self.completion_time = clock.get_clock_minutes() - self.schedule
            self.status = Order_Status.Concluded.value
    

    def inProgress(self):
        with self.l:
            print(f"In Progress Id:{self.id}")
            self.status = Order_Status.In_Progress.value
    

    def setVehicle(self, vehicle_id:int):
        with self.l:
            self.vehicle_id = vehicle_id


    def isComplete(self) -> bool:
        with self.l:
            return self.status == Order_Status.Concluded.value
    

    def isAvailable(self) -> bool:
        with self.l:
            return self.status == Order_Status.Pendent.value


    def getPriority(self):
        with self.l:
            return self.priority
    
    def __eq__(self, other):
        if not isinstance(other, Order):
            return False
        return self.id == other.id
