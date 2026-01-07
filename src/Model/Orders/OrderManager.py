from src.Model.Graph.Graph import Graph
from src.Model.Graph.Node import Node
from src.Model.Taxi.Taxi import Taxi
from src.Model.Timer.Clock import Clock
from src.View.Viewer import Viewer
from src.Model.Orders.Order import Order,Order_Status
import random
from typing import List
import sys
from threading import Barrier
from collections import deque



class OrderManager:
    
    def __init__(self, crs):
        self.orders = list()
        self.priority_orders = list()
        self.terminated_orders = list()
        self.next_order_id = 1
        self.crs = crs
        self.rng = random.Random(30)
    
    def generateOrders(self, graph:Graph, digital_clock_time: int, clock:Clock) -> list[Order]:
        nodes:list[int] = list(graph.m_nodes.keys())

        orders_number = self.activity_function_Orders(digital_clock_time)
        orders = list()
        for i in range(orders_number):
            choice_source:int = self.rng.choice(nodes)
            choice_destination:int = self.rng.choice(nodes)
            while(choice_source == choice_destination):
                choice_source = self.rng.choice(nodes)
            
            node:Node = graph.m_nodes[choice_source]

            choice_passengers = self.rng.randint(1,4) 
            choice_id = self.next_order_id
            self.next_order_id += 1
            order = Order(choice_id,self.crs,choice_source, choice_destination, choice_passengers,digital_clock_time,1,position=node.get_position())
            orders.append(order)
        
        return orders

            
    def pending_orders(self):
        return [p for p in self.orders if p.status == Order_Status.Pendent.value]
    
    def activity_function_Orders(self,digital_clock_time:int):
        return 5

    def choose_next_order(self):
        pending = self.pending_orders()
        if not pending:
            return None

        pending.sort(key=lambda p: (-p.priority, p.schedule))
        return pending[0]

    def giveOrder(self, taxi:Taxi, order:Order):
        print("set")
        taxi.setOrder(order)


    def give_order_to_best_taxi(self, taxis: list[Taxi], graph: Graph, order: Order, search_algorithm) -> bool:
        destination = order.get_destination()
        best_cost, best_choice_taxi = sys.maxsize, None

        for taxi in taxis:
            
            if taxi.isAvailable():
                result = graph.search_path(search_algorithm, taxi.getNode(), destination)
                
                if result is None:
                    
                    continue

                path, cost, distance = result
                if cost < best_cost:
                    best_cost, best_choice_taxi = cost, taxi

        if best_choice_taxi is None:
            return False  
        
        order.setVehicle(best_choice_taxi.get_id())
        self.giveOrder(best_choice_taxi, order)
        return True



    def start_activity(self, taxis: List[Taxi], turn_barrier: Barrier, clock: Clock, graph: Graph, viewer:Viewer, seach_algorithm:int):
        
        old_time = -1
        while True:
            time = clock.get_clock_time()
            if(old_time != time):
                new_orders = self.generateOrders(graph,time,clock) 
                
                for new_order in new_orders:
                    graph.add_order(new_order)
                    viewer.add_Order(new_order)

                    if new_order.getPriority() == 0:
                        self.orders.append(new_order)
                    else:
                        self.priority_orders.append(new_order)
            
                old_time = time

            self.give_priority_orders(taxis,graph, seach_algorithm)

            if self.priority_orders.__len__() == 0:
                self.give_normal_orders(taxis,graph,seach_algorithm)

            
            turn_barrier.wait()


    def give_priority_orders(self, taxis, graph, search_algorithm) -> bool:
        i = 0
        for order in self.priority_orders:
            if self.give_order_to_best_taxi(taxis,graph,order,search_algorithm):
                self.priority_orders.remove(order)
                self.terminated_orders.append(order)
            
            i += 1
        
        return i == 0
    
    def give_normal_orders(self, taxis, graph, search_algorithm) -> bool:
        i = 0
        for order in self.orders:
            if self.give_order_to_best_taxi(taxis,graph,order,search_algorithm):
                self.orders.pop(i)
                self.terminated_orders.append(order)
            
            i += 1
        
        return i == 0

    