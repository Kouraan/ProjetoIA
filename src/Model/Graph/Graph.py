from src.Model.Graph.Node import Node
from typing import Dict, List, Tuple
from src.Model.Graph.Edge import Edge
from threading import Lock
import pandas

class Graph:
    def __init__(self, directed=False):
        self.m_nodes = {}  # nodes list id:Node
        self.m_edges = {}  # edeges list id:Edge
        self.m_graph:Dict[int, List[Tuple[Edge, int]]] = {}  # adjadency graph Node_id: [Edge, Node_id]
        self.m_directed = directed
        self.l = Lock()

    def add_node(self, node_id: int, x: float, y: float):
        if node_id not in self.m_nodes:
            node = Node(node_id, x, y)
            self.m_nodes[node_id] = node     
            self.m_graph[node_id] = []        
    
    def add_edge(self, source_id: int, destination_id: int,max_speed: int, length: float, positions):
        
        if source_id not in self.m_nodes:
            print(f"Source node {source_id} does not exist.")
            return
        if destination_id not in self.m_nodes:
            print(f"Destination node {destination_id} does not exist.")
            return

        edge = Edge(source_id, destination_id, max_speed, length, positions)
        self.m_graph[source_id].append((edge,destination_id))

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



    

    def search_path(self,search_algorithm:int, start:int,target:int):
        match search_algorithm:
            case 1:
                return self.dfsAlgorithm(start,target)
        pass



    def __str__(self):
        solution =''

        for m_node in self.m_nodes:
            solution = f"{m_node}"
        solution = f"{solution}\n"

        solution = f"{solution} {self.m_graph}"

        return solution
    
        

        
    def dfsAlgorithm(self, start: int, destination: int):
        stack = [(start, [], 0)]  
        visited = set()

        while stack:
            node, path_edges, weight = stack.pop()

            if node in visited:
                continue
            visited.add(node)

            if node == destination:
                return path_edges, weight

            for edge, neighbour in self.get_Neighbours(node):
                if neighbour not in visited:

                    new_path_edges = path_edges + [(node, edge)]
                    stack.append((neighbour, new_path_edges, weight + edge.weightFunction()))

        return None

    
