from shapely import LineString
from threading import Lock

class Edge:
    def __init__(self, source_id:int, destination_id:int,max_speed:int, length:float, positions : LineString):
        #print(max_speed)
        self.source_id = source_id
        self.destination_id = destination_id
        self.max_speed = max_speed
        self.length = length
        self.positions = positions
        self.l = Lock()
    
    def __str__(self):
        with self.l:
            return f"{self.source_id} -|- {self.destination_id}  -|- {self.max_speed} -|- {self.length} -|- {self.positions}"

    def getDestination(self):
        with self.l:
            return self.source_id
    
    def weightFunction(self):
        with self.l:
            return 5

    def getSpeed(self):
        with self.l:
            return self.max_speed