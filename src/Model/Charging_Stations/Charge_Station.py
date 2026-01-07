from enum import Enum
import time as tm
from threading import Barrier
from src.Util.coordinates_util import to_latlon

class StationType(Enum):
    PETROL = "petroleum"
    ELECTRIC = "electric"


class Charge_Station:
    def __init__(self, crs, position:tuple[float,float],turns:int):
        self.crs = crs
        self.position = to_latlon(crs, position[0], position[1])
        self.type = None
        self.charge_rate = 1

    def charge(self, turns:int, barrier:Barrier):
        for i in range(turns*self.charge_rate):
            barrier.wait()


class Petroleum_Station(Charge_Station):
    def __init__(self, crs, position, barrier):
        super().__init__(crs, position, barrier)
        self.type = StationType.PETROL
        self.charge_rate = 1

    def charge(self, turns):
        super().charge(turns)


class Eletrical_Station(Charge_Station):
    def __init__(self, crs, position, barrier):
        super().__init__(crs, position, barrier)
        self.type = StationType.ELECTRIC
        self.charge_rate = 10
