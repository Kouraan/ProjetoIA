from enum import Enum
import time as tm
from threading import Barrier,Lock
from src.Util.coordinates_util import to_latlon



class StationType(Enum):
    PETROL = "petroleum"
    ELECTRIC = "electric"


class Charge_Station:
    def __init__(self, crs, position:tuple[float,float],turns:int, type:str):
        self.crs = crs
        self.position = to_latlon(crs, position[0], position[1])
        self.type = type
        self.charge_rate = 1
        self.l = Lock()

    def charge(self, barrier:Barrier):
        print("Recharging")
        if self.type == StationType.PETROL.value:
            for i in range(self.charge_rate):
                barrier.wait()

        if self.type == StationType.ELECTRIC.value:
            for i in range(20*self.charge_rate):
                barrier.wait()


    def to_dict(self):
        with self.l:
            return {
                "position": self.position,
                "type": self.type
            }
