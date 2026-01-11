from src.Model.Orders.Order import Order
from src.Model.Graph.Node import Node
from src.Model.Graph.Edge import Edge
from typing import Deque, Dict, List, Tuple
from collections import deque
from threading import Lock
from src.Model.Charging_Stations.Charge_Station import Charge_Station,StationType

import pandas
import heapq
import random


class Graph:
    def __init__(self, directed=False):
        self.m_nodes:Dict[int,Node] = {}  # nodes list id:Node
        self.m_edges = [] 
        self.m_graph:Dict[int, List[Tuple[Edge, int]]] = {}  # adjadency graph Node_id: [Edge, Node_id]
        self.charging_nodes: Dict[int, Charge_Station]= {}
        self.m_orders: Dict[int, list[Order]] = {}
        self.weigth_rate_Ambiental_Impact = 0
        self.weigth_rate_Cost = 0
        self.weigth_rate_Speed = 0


        self.weigth_rate_Ambiental_Impact = 0
        self.m_directed = directed
        self.l = Lock()

    def add_node(self, node_id: int, x: float, y: float):
        if node_id not in self.m_nodes:
            node = Node(node_id, x, y)
            self.m_nodes[node_id] = node     
            self.m_graph[node_id] = []        
    
    def add_edge(self, source_id: int, destination_id: int,max_speed: int, length: float, positions, oneway:bool):
        
        if source_id not in self.m_nodes:
            print(f"Source node {source_id} does not exist.")
            return
        if destination_id not in self.m_nodes:
            print(f"Destination node {destination_id} does not exist.")
            return

        edge = Edge(source_id, destination_id, max_speed, length, positions)
        self.m_edges.append(edge)
        if oneway:
            self.m_graph[source_id].append((edge,destination_id))
        else :
            self.m_graph[source_id].append((edge,destination_id))
            self.m_graph[destination_id].append((edge,source_id))


    def get_all_orders(self):
        result: list[Order] = [order for lista in self.m_orders.values() for order in lista]
        return result
    
    def add_order(self, order:Order):
        with self.l:
            source = order.get_source()
            if source not in self.m_orders:
                self.m_orders[source] = []
            self.m_orders[source].append(order)



    def get_Neighbours(self,node_id:int) -> List[Tuple[Edge, int]]:
        return self.m_graph[node_id]


    def getNode(self, node_id:int) -> Node:
        with self.l:
            return self.m_nodes[node_id]

    def get_Node_Edge(self, source_id:int, target_id:int) -> Edge:
        with self.l:
            neighbours = self.m_graph[source_id] 

            for edge,destination in neighbours:
                if destination == target_id:
                    return edge
                


    def generate_charging_stations(self, n: int):
        result = list()
        for _ in range(n):
            choice_source: int = random.choice(list(self.m_nodes.keys()))
            charge_station: Charge_Station = Charge_Station("EPSG:32629",self.m_nodes[choice_source].get_position(),5,random.choice(["petroleum","electric"]))
            self.charging_nodes[choice_source] = charge_station
            result.append(charge_station)

        return result



    def euclidean_distance(self,n1:int, n2:int) :
        x1,y1 = self.m_nodes[n1].get_position()
        x2,y2 = self.m_nodes[n2].get_position()

        return ((x1 - x2)**2 + (y1 - y2)**2) ** 0.5
    

    
    def heuristic(self,n1:int,n2:int, current_autonomy:int , max_autonomy:int, passengers:int, passengers_cap:int,orders:list[Order]):
        distance_to_goal = self.euclidean_distance(n1,n2) * (current_autonomy/max_autonomy)
        if current_autonomy < distance_to_goal:
            distance_to_station = min([self.euclidean_distance(n1, station) for station in self.charging_nodes.keys()])
            distance_to_goal += distance_to_station
        
        order_weight = 0.0
        if passengers_cap > 0:
            for order in orders:
                order_passengers = order.get_passengers()
                if order_passengers + passengers > passengers_cap:
                    continue

                dist_pickup = self.euclidean_distance(n1, order.get_source())
                dist_dropoff = self.euclidean_distance(n2, order.get_destination())
                distance_to_order = min(dist_pickup, dist_dropoff)

                if distance_to_order < distance_to_goal:
                    order_weight += order_passengers / (1 + distance_to_order)

        return distance_to_goal -  0.1*order_weight




    def reconstruct_path(self, came_from: dict, current: int):
        path_edges = []

        while current in came_from:
            prev_node, edge = came_from[current]
            path_edges.append((prev_node, edge))
            current = prev_node

        path_edges.reverse()
        return path_edges




    def search_Algorithms(self,search_algorithm:int, start:int,target:int,reserve_autonomy:float):
        match search_algorithm:
            case 1:
                return self.dfs(start,target,reserve_autonomy)
        pass
    
    def prepare_charging(self, start:int, autonomy:int,search_algorithm:int, type:StationType):
        with self.l:
            min_distance = 0
            min_cost = float('inf')
            min_path = None
            for station in self.charging_nodes.keys():
                if self.charging_nodes[station].type == type:
                    path,cost,distance = self.search_path(search_algorithm, start, station)
                    
                    if distance > autonomy:
                        continue
                    else:
                        if min_cost > cost:
                            min_path,min_cost,min_distance = path,cost,distance
            
            return min_path,min_cost,min_distance


    def search_path(self,search_algorithm:int, start:int,target:int, passengers:int = 0, capacity:int=0, autonomy:int=1000,maxAutonomy:int = 1000) -> tuple[list[Edge], int, int]:
        match search_algorithm:
            case 1:
                return self.dfsAlgorithm(start,target)
            case 2:
                return self.bfsAlgorithm(start,target)
            case 3:
                return self.a_star_Algorithm(start,target, passengers, capacity,autonomy,maxAutonomy)

        


    
        
    def dfs(self, start, destination, autonomy):
        result = self.dfsAlgorithm(start, destination)
        if result is None:
            return None
        
        path, cost, dist = result
        if dist <= autonomy:
            return path, cost, dist

        best = None
        best_cost = float('inf')

        for station in self.charging_nodes:
            r1 = self.dfsAlgorithm(start, station)
            if not r1:
                continue
            path1, cost1, dist1 = r1
            if dist1 > autonomy:
                continue

            r2 = self.dfsAlgorithm(station, destination)
            if not r2:
                continue
            path2, cost2, dist2 = r2
            if dist2 > autonomy:
                continue

            total_cost = cost1 + cost2
            total_dist = dist1 + dist2
            full_path = path1 + path2

            if total_cost < best_cost:
                best = (full_path, total_cost, total_dist)
                best_cost = total_cost

        return best




    def dfsAlgorithm(self, start: int, destination: int):
        stack:list[tuple[int, list[Edge], int, int]] = [(start, [], 0, 0)]  # node, path, weight, distance
        visited = set()

        while stack:
            node, path_edges, weight, distance = stack.pop()

            if node in visited:
                continue
            visited.add(node)

            if node == destination:
                return path_edges, weight, distance

            for edge, neighbour in self.get_Neighbours(node):
                if neighbour not in visited and edge.get_Activity():
                    new_path_edges = path_edges + [(neighbour, edge)]
                    stack.append((neighbour, new_path_edges, weight + edge.weightFunction(), distance + edge.getLength()))

        return None





    def bfsAlgorithm(self, start: int, destination: int):
        queue = deque()
        queue.append((start, []))
        visited = {start}

        while queue:
            node, path_edges = queue.popleft()

            if node == destination:
                total_cost = sum(edge.weightFunction() for _, edge in path_edges)
                total_dist = sum(edge.getLength() for _, edge in path_edges)
                return path_edges, total_cost, total_dist

            for edge, neighbour in self.get_Neighbours(node):
                if neighbour not in visited and edge.get_Activity():
                    visited.add(neighbour)
                    new_path = path_edges + [(node, edge)]
                    queue.append((neighbour, new_path))

        return None





    def a_star_Algorithm(self, start: int, destination: int, passengers:int, passengers_cap:int, autonomy:int, maxAutonomy:int):
        all_orders = self.get_all_orders()
        open_set = []
        heapq.heappush(open_set, (0, start))

        came_from = {}            
        g_score = {start: 0}         
        dist_score = {start: 0}

        while open_set:
            _, node = heapq.heappop(open_set)

            if node == destination:
                path = self.reconstruct_path(came_from, node)
                total_weight = g_score[node]
                total_distance = dist_score[node]
                return path, total_weight, total_distance

            for edge, neighbour in self.get_Neighbours(node):
                tentative_g = g_score[node] + edge.weightFunction()
                tentative_d = dist_score[node] + edge.getLength()

                if tentative_g < g_score.get(neighbour, float('inf')):
                    came_from[neighbour] = (node, edge)
                    g_score[neighbour] = tentative_g
                    dist_score[neighbour] = tentative_d
                    f = tentative_g + self.heuristic(neighbour, destination,autonomy, maxAutonomy,passengers,passengers_cap,all_orders)
                    heapq.heappush(open_set, (f, neighbour))

        return None

    



    def __str__(self):
        solution =''

        for m_node in self.m_nodes:
            solution = f"{m_node}"
        solution = f"{solution}\n"

        solution = f"{solution} {self.m_graph}"

        return solution


    def pick_order_decision(self, current_node, destination_node, passengers_capacity:int) -> Order:
        if current_node not in self.m_orders:
            return None

        for order in self.m_orders[current_node]:
            if not order.isAvailable():
                continue

            distance = self.euclidean_distance(current_node, destination_node)
            order_distance = self.euclidean_distance(destination_node, order.get_destination())

            if passengers_capacity < order.get_passengers(): continue
            if distance < order_distance: continue
            print(f"Picked Order {order.get_source()}")
            order.inProgress()
            return order
        
        return None
    

    def recharge_choice_decision(self, current_node,destination_node,autonomy:float,isRecharginPath:bool = False):
        if current_node not in self.charging_nodes:
            return None

        distance = self.euclidean_distance(current_node, destination_node)
        if isRecharginPath:
            return self.charging_nodes[current_node]
        if autonomy > distance*3:
            return None
        else:
            return self.charging_nodes[current_node]
        