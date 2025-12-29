from src.Model.Graph.Graph import Graph
from src.Model.Graph.Node import Node
from src.Model.Taxi.Taxi import Taxi
from src.Model.Timer.Clock import Clock
from src.Model.Orders.Order import Order,Order_Status
import random
from typing import List
import sys
from threading import Barrier
from collections import deque



class OrderManager:
    
    def __init__(self):
        self.orders = deque()
        self.next_order_id = 1

    
    def generateOrders(self, graph:Graph, digital_clock_time: int) -> list[Order]:
        nodes:list[int] = list(graph.m_nodes.keys())

        orders_number = self.activity_function_Orders(digital_clock_time)
        orders = list()
        for i in range(orders_number):
            choice_source:int = random.choice(nodes)
            choice_destination:int = random.choice(nodes)

            while(choice_source == choice_destination):
                choice_source = random.choice(nodes)
            
            choice_passengers = random.randint(1,4) 
            choice_id = self.next_order_id
            self.next_order_id += 1
            order = Order(choice_id,choice_source, choice_destination, choice_passengers,digital_clock_time,1)
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
        taxi.setOrder(order)


    def give_order_to_best_taxi(self, taxis: list[Taxi], graph: Graph, order: Order) -> bool:
        destination = order.get_destination()
        best_cost, best_choice_taxi = sys.maxsize, None

        for taxi in taxis:
            if taxi.isAvailable():
                result = graph.search_path(1, taxi.getNode(), destination)
                if result is None:
                    continue

                path, cost = result
                if cost < best_cost:
                    best_cost, best_choice_taxi = cost, taxi

        if best_choice_taxi is None:
            return False  

        self.giveOrder(best_choice_taxi, order)
        return True



    def start_activity(self, taxis: List[Taxi], turn_barrier: Barrier, clock: Clock, graph: Graph):
        while True:
            time = clock.get_clock_time()

            for _ in range(len(self.orders)):
                order = self.orders.popleft()
                if not self.give_order_to_best_taxi(taxis, graph, order):
                    self.orders.append(order)

            new_orders: list[Order] = self.generateOrders(graph, time)
            for order in new_orders:
                if not self.give_order_to_best_taxi(taxis, graph, order):
                    self.orders.append(order)

            turn_barrier.wait()



        
