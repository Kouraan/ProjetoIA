from shapely import LineString
from threading import Lock
import sys
class Edge:
    def __init__(self, source_id:int, destination_id:int,max_speed:int, length:float, positions : LineString):
        self.source_id = source_id
        self.destination_id = destination_id
        self.max_speed = max_speed
        self.length = length
        self.congestion = 1
        self.positions = positions
        self.l = Lock()
        self.active = True
    
    def __str__(self):
        with self.l:
            return f"{self.source_id} -|- {self.destination_id}  -|- {self.max_speed} -|- {self.length} -|- {self.positions}"

    def getDestination(self):
        with self.l:
            return self.source_id
    
    def getLength(self):
        with self.l:
            return self.length

    def getSpeed(self):
        with self.l:
            return self.max_speed
    
    def weightFunction(self):
        with self.l:
            if self.active == False:
                return sys.float_info.max
            return self.length/(self.max_speed*self.congestion)
    
    def setCongestion(self, rate:float):
        with self.l:
            self.congestion = rate
    
    def set_Inactive(self):
        with self.l:
            self.active = False
    

    def reset_status(self):
        with self.l:
            self.congestion = 1
            self.active = True
    

    def get_Activity(self):
        with self.l:
            return self.active