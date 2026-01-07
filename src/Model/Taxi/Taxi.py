from enum import Enum
from queue import Queue
import random
from src.Model.Graph.Node import Node
from src.Model.Graph.Edge import Edge
from src.Model.Graph.Graph import Graph
from src.Model.Orders.Order import Order

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

    def __init__(self, id:int, currentNode:Node, tipo, max_autonomy, capacity , custoKm, impAmbiental, autonomy:float = 0, crs = None):
        self.id:int = id
        self.tipo:int = Taxi_Type(tipo).value
        self.autonomy:float = autonomy        
        self.max_autonomy:float = max_autonomy
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

    def start_simultation(self,graph:Graph,barrier:Barrier,search_algorithm:int, atualization_rate:float):
        atualization = 1/atualization_rate
        while self.Running.is_set():
            self.waitOrder(barrier)
            order:Order = self.orders.pop(0)
            self.simulation(atualization,order.get_source(),graph,search_algorithm,barrier)
            self.simulation(atualization,order.get_destination(),graph,search_algorithm,barrier)
            order.complete()
            self.disponibility = disponibility.Free.value 

    def simulation(self, update_time, target:int, graph:Graph, search_algorithm:int,barrier:Barrier):

        current_distance = 0
        r = graph.search_path(search_algorithm,start=self.currentNode,target=target,passengers=self.passengers,capacity=self.capacity)

        if r is None:
            return
        
        path,cost,distance = r

        #if self.autonomy < distance:
            # graph.prepare_charging(self.currentNode, self.autonomy,search_algorithm) 

        for next_node_id,edge in path:
            new_order = graph.pick_order_decision(next_node_id,target,self.capacity)
            if new_order is not None: 
                self.setOrder(new_order)
                self.passengers += new_order.get_passengers()

            current_distance = self.move(edge=edge,dt=update_time, barrier=barrier)
            self.setNode(next_node_id)


    def waitOrder(self, barrier: Barrier):
        while True:
            with self.lock:
                if self.orders.__len__() != 0:
                    print(self.orders.__len__())
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


    
    
    def move(self, edge: Edge, dt: int, barrier: Barrier):
        total_length = edge.getLength()

        start_distance = edge.positions.project(Point(self.position))
        
        current_distance = start_distance

        while current_distance < total_length:
            moved_distance = (float(edge.getSpeed()) / 3.6) * dt
            remaining = total_length - current_distance
            moved_distance = min(moved_distance, remaining)

            # # Checa autonomia
            # if self.autonomy >= moved_distance:
            #     self.autonomy -= moved_distance
            # else:
            #     moved_distance = self.autonomy
            #     self.autonomy = 0
            #     current_distance += moved_distance
            #     break

            current_distance += moved_distance

            if edge.positions is not None:
                new_position = edge.positions.interpolate(current_distance)
                self.position = new_position.coords[0]

            
            try:
                barrier.wait()
            except BrokenBarrierError:
                break

        return current_distance


    def to_dict(self):
        with self.lock:
            return {
                "id": self.id,
                "tipo": self.tipo,
                "position": to_latlon(self.crs,self.position[0], self.position[1]),
                "autonomy": self.autonomy,
                "max_autonomy": self.max_autonomy,
                "capacity": self.capacity,
                "custoKm": self.custoKm,
                "impactoAmbiental": self.impAmbiental,
                "disponibility": self.disponibility
            }

