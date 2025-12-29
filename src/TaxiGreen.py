from src.Model.Graph.Graph import Graph
from src.Model.Graph.Node import Node
from src.Model.Taxi.Taxi import *
from src.Model.Orders.OrderManager import OrderManager
from src.Model.Timer.Clock import Clock
import numpy as np
import osmnx as ox
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
from threading import Thread,Barrier
import random
import pandas
class TaxiGreen:

    def __init__(self,number_of_taxis:int):
        self.generate_Graph()
        self.turn_barrier = Barrier(number_of_taxis+1+1) # number of threads simulating. taxis + thread simulating clock
        self.clock = Clock(turn_barrier=self.turn_barrier)
        self.taxis:list[Taxi] = self.generate_taxis(number_of_taxis)
        self.order_manager:OrderManager = OrderManager()
        self.active_threads_number = 0
    

    def generate_Graph(self):
        G = ox.graph_from_place('Braga, Portugal', network_type='drive')
        G_Meters = ox.project_graph(G)
        nodes,edges = ox.graph_to_gdfs(G_Meters)

        G_new = Graph()


        for node_id,node in nodes.iterrows():
            G_new.add_node(node_id, node['x'],node['y'])

        with open("edges.txt", "w", encoding="utf-8") as f:
            for (u,v,k),edge in edges.iterrows():
                maxspeed = edge['maxspeed']



                if isinstance(maxspeed, list):
                    maxspeed = maxspeed[0]

                if maxspeed is None or pandas.isna(maxspeed):
                    maxspeed = 50

                f.write(
                f"{u},{v},{k},"
                f"maxspeed={maxspeed},"
                f"length={edge['length']},"
                f"geometry={edge['geometry']}\n"
                )

                G_new.add_edge(u,v,maxspeed,edge['length'],edge['geometry'])
            
            self.graph = G_new


    def generate_taxis(self, number_of_taxis:int):
        nodes:list[Node] = list(self.graph.m_nodes.values())
        taxis = list()

        for i in range(number_of_taxis):
            initial_node = nodes[random.randint(0, self.graph.m_nodes.__len__())] 
            taxi_type = random.randint(1,2)
            autonomy = random.randint(2000,2500)
            capacity = random.randint(1,4)
            kmCost = random.randint(1,5)
            ambiental_impact = round(random.random(), 2)
            taxi = Taxi(i,initial_node,taxi_type,autonomy, capacity, kmCost,ambiental_impact)
            taxis.append(taxi)
        
        return taxis

    

    def start_simulation(self):
        clock_thread = Thread(target=self.clock.start_clock_task)
        self.active_threads_number += 1
        order_manager_thread = Thread(target=self.order_manager.start_activity,args=(self.taxis,self.turn_barrier,self.clock,self.graph))
        self.active_threads_number += 1
        taxi_Threads = list()
        clock_thread.start()
        order_manager_thread.start()

        for taxi in self.taxis:
            taxi_Thread = Thread(target=taxi.start_simultation,args=(self.graph,self.turn_barrier))
            taxi_Thread.start()
            taxi_Threads.append(taxi_Thread)
            self.active_threads_number += 1
        
    

        
    
        

