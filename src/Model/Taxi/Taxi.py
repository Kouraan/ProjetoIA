from enum import Enum
from src.Model.Graph.Node import Node
from src.Model.Graph.Edge import Edge
from src.Model.Graph.Graph import Graph
from src.Model.Orders.Order import Order
from shapely import *
from threading import Lock,Condition,Barrier

class Taxi_Type(Enum):
    Combustion = 1
    Eletric = 2

class disponibility(Enum):
    Free = 1
    Busy = 2
    Charging = 3



class Taxi:

    def __init__(self, id:int, currentNode:Node, tipo, max_autonomy, capacity , custoKm, impAmbiental, autonomy:float = 0):
        self.id = id
        self.tipo = Taxi_Type(tipo).value
        self.autonomy = autonomy        
        self.max_autonomy = max_autonomy
        self.custoKm = custoKm
        self.position = currentNode.get_position()  
        self.capacity:int = capacity     
        self.impAmbiental:int = impAmbiental   
        self.disponibility:int = disponibility.Free
        self.currentNode:int = currentNode.get_id()
        self.order:Order = None
        self.lock:Lock = Lock()
        self.order_exists_condition:Condition = Condition(self.lock)
    
    def move(self, edge:Edge,dt:int, current_distance:float, barrier:Barrier):
        current_distance = 0
        while True:
            moved_distance = (float(edge.getSpeed())/3.6)*dt


            # if self.autonomy >= moved_distance:
            #     self.autonomy -= moved_distance
            # else:
            #     moved_distance = self.autonomy
            #     self.autonomy = 0
        
            current_distance += moved_distance

            new_position = edge.positions.interpolate(min(current_distance, edge.length))
            self.position = new_position.coords[0]
            if (current_distance) >= edge.length:
                break
            
            #print("waiting")
            barrier.wait()
        



    def start_simultation(self,graph:Graph,barrier:Barrier):
        while True:
            self.waitOrder(barrier)
            self.simulation(60,self.order.get_source(),graph,1,barrier)
            self.simulation(60,self.order.get_destination(),graph,1,barrier)
   
    def simulation(self, update_time, target:int, graph:Graph, search_algorithm:int,barrier:Barrier) -> int:
        current_distance = 0
        path,cost = graph.search_path(search_algorithm,self.currentNode,target)

        for next_node_id,edge in path:
            current_distance = self.move(edge=edge,dt=update_time, current_distance=current_distance, barrier=barrier)
            self.setNode(next_node_id)
        
        print("Completed")
            

    def setOrder(self, order: Order):
        with self.lock:
            self.order = order
    

    def waitOrder(self, barrier: Barrier):
        while True:
            with self.lock:
                if self.order is not None:
                    break
                #print("wait")
            
            barrier.wait()
        
    def setNode(self, node_id:int):
        with self.lock:
            self.currentNode = node_id
        
    def getNode(self):
        with self.lock:
            return self.currentNode

    def isAvailable(self):
        with self.lock:
            return self.disponibility == disponibility.Free