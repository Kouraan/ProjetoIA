from enum import Enum
from queue import Queue
import random
from src.Model.Graph.Node import Node
from src.Model.Graph.Edge import Edge
from src.Model.Graph.Graph import Graph
from src.Model.Charging_Stations.Charge_Station import Charge_Station,StationType
from src.Model.Orders.Order import Order
from src.Model.Timer.Clock import Clock

from shapely import *
from threading import BrokenBarrierError, Lock,Condition,Barrier,Event
from src.Util.coordinates_util import to_latlon

class Taxi_Type(Enum):
    Combustion = 1
    Eletric = 2

class disponibility(Enum):
    Free = 1
    Busy = 2
    Charging = 3



class Taxi:

    def __init__(self, id:int, currentNode:Node, tipo, max_autonomy, capacity , custoKm, impAmbiental, crs = None):
        self.id:int = id
        self.tipo:int = Taxi_Type(tipo).value
        self.autonomy:float = max_autonomy * 1000       
        self.max_autonomy:float = max_autonomy * 1000
        self.custoKm:float = custoKm
        self.position:tuple[float,float] = currentNode.get_position()  
        self.capacity:int = capacity 
        self.passengers:int = 0    
        self.impAmbiental:int = impAmbiental   
        self.disponibility:int = disponibility.Free.value
        self.currentNode:int = currentNode.get_id()
        self.orders: list[Order] = list()
        self.crs:int = crs
        self.lock:Lock = Lock()
        self.orders_exists_condition:Condition = Condition(self.lock)
        self.Running = Event()
        self.Running.set()
        print(self.crs)
    


    def get_id(self):
        with self.lock:
            return self.id

    def setOrder(self, order: Order):
        with self.lock:
            self.disponibility = disponibility.Busy.value
            self.orders.append(order)

    def start_simultation(self,graph:Graph,barrier:Barrier,search_algorithm:int, atualization_rate:float, clock:Clock):
        
        atualization = 60.0

        while clock.get_Running():
            self.waitOrder(barrier)
            order:Order = self.orders.pop(0)
            self.simulation(atualization,order.get_source(),graph,search_algorithm,barrier)
            self.simulation(atualization,order.get_destination(),graph,search_algorithm,barrier)
            order.complete(clock)

            self.disponibility = disponibility.Free.value

    def simulation(self, update_time: float, target: int, graph: Graph, search_algorithm: int, barrier: Barrier):
        r = graph.search_path(search_algorithm, start=self.currentNode, target=target,
                            passengers=self.passengers, capacity=self.capacity)
        if r is None:
            return

        path, cost, distance = r
        recharging = False
        if self.autonomy < distance:
            recharging = True
            graph.prepare_charging(self.currentNode, self.autonomy, search_algorithm, StationType.PETROL)

        overflow = 0.0
        for next_node_id, edge in path:
            if not edge.get_Activity():
                self.simulation(update_time, target, graph, search_algorithm, barrier)
                break

            new_order = graph.pick_order_decision(next_node_id, target, self.capacity)
            if new_order is not None:
                self.setOrder(new_order)
                self.passengers += new_order.get_passengers()

            station: Charge_Station = graph.recharge_choice_decision(self.currentNode, target, self.autonomy, recharging)
            if station:
                station.charge(barrier)
                self.autonomy = self.max_autonomy

            overflow = self.move(edge, dt=update_time, barrier=barrier, current_distance=overflow)

            self.setNode(next_node_id)


    def waitOrder(self, barrier: Barrier):
        while True:
            with self.lock:
                if self.orders.__len__() != 0:
                    self.disponibility = disponibility.Busy.value
                    break
            try:
                barrier.wait()
            except BrokenBarrierError:
                break
        
    def setNode(self, node_id:int):
        with self.lock:
            self.currentNode = node_id
        
    def getNode(self):
        with self.lock:
            return self.currentNode

    def isAvailable(self):
        with self.lock:
            return self.disponibility == disponibility.Free.value
    

    def copy(self):
        return Taxi(self.id,self.currentNode,self.tipo,self.max_autonomy,self.capacity,self.custoKm,self.impAmbiental,self.autonomy)
    

    def stop(self):
        self.Running.clear()


    
    
    def move(self, edge: Edge, dt: float, barrier: Barrier, current_distance: float = 0.0):
        total_length = edge.getLength()
        moved_distance = (edge.getSpeed() / 3.6) * dt

        while moved_distance > 0 and self.autonomy > 0:
            remaining = total_length - current_distance
            step = min(moved_distance, remaining, self.autonomy)

            with self.lock:
                self.autonomy -= step
                current_distance += step
                if edge.positions is not None:
                    self.position = edge.positions.interpolate(current_distance).coords[0]

            try:
                barrier.wait()
            except BrokenBarrierError:
                break

            moved_distance -= step

            if current_distance >= total_length:
                overflow = moved_distance
                current_distance = 0 
                return overflow  

        return 0  


    def to_dict(self):
        with self.lock:
            position_latlon = to_latlon(self.crs, self.position[0], self.position[1])
            return {
                "id": self.id,
                "tipo": self.tipo,
                "position": list(position_latlon) if position_latlon else [0, 0],
                "autonomy": self.autonomy,
                "max_autonomy": self.max_autonomy,
                "capacity": self.capacity,
                "custoKm": self.custoKm,
                "impactoAmbiental": self.impAmbiental,
                "disponibility": self.disponibility
            }

