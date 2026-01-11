from src.Model.Graph.Graph import Graph
from src.Model.Taxi.Taxi import Taxi
from src.Model.Timer.Clock import Clock
from src.View.Viewer import Viewer
from src.Model.Orders.Order import Order, Order_Status
from threading import Barrier, Event
from typing import List
import random
import sys

class OrderManager:
    def __init__(self, crs):
        self.orders = []  # lista completa de todas as orders
        self.priority_orders = []  # orders pendentes de prioridade
        self.terminated_orders = []  # orders concluídas
        self.next_order_id = 1
        self.crs = crs
        self.rng = random.Random(30)
        self.running = Event()
        self.running.set()

    def generateOrders(self, graph: Graph, digital_clock_time: int, clock: Clock) -> List[Order]:
        nodes = list(graph.m_nodes.keys())
        creation_time = clock.get_clock_minutes()
        orders_number = self.activity_function_Orders(digital_clock_time)
        orders = []
        for _ in range(orders_number):
            source = self.rng.choice(nodes)
            dest = self.rng.choice(nodes)
            while dest == source:
                dest = self.rng.choice(nodes)
            node = graph.m_nodes[source]
            passengers = self.rng.randint(1,4)
            order_id = self.next_order_id
            self.next_order_id += 1
            order = Order(order_id, self.crs, source, dest, passengers, creation_time, 1, position=node.get_position())
            orders.append(order)
        return orders

    def pending_orders(self):
        return [p for p in self.orders if p.status == Order_Status.Pendent.value]

    def activity_function_Orders(self, digital_clock_time: int):
        return 5

    def giveOrder(self, taxi: Taxi, order: Order):
        taxi.setOrder(order)

    def give_order_to_best_taxi(self, taxis: List[Taxi], graph: Graph, order: Order, search_algorithm) -> bool:
        best_cost, best_choice = sys.maxsize, None
        for taxi in taxis:
            if taxi.isAvailable():
                result = graph.search_path(search_algorithm, taxi.getNode(), order.get_destination())
                if result is None:
                    continue
                path, cost, distance = result
                if cost < best_cost:
                    best_cost, best_choice = cost, taxi
        if best_choice is None:
            return False
        order.setVehicle(best_choice.get_id())
        self.giveOrder(best_choice, order)
        return True

    def start_activity(self, taxis: List[Taxi], turn_barrier: Barrier, clock: Clock, graph: Graph, viewer: Viewer, search_algorithm: int):
        old_time = -1
        while self.running.is_set():
            time = clock.get_clock_time()
            self.update_terminated_orders() 
            if old_time != time:
                new_orders = self.generateOrders(graph, time, clock)
                for order in new_orders:
                    graph.add_order(order)
                    viewer.add_Order(order)
                    self.orders.append(order)  # mantém todas as orders
                    if order.getPriority() > 0:
                        self.priority_orders.append(order)
                old_time = time
            self.give_priority_orders(taxis, graph, search_algorithm)
            if len(self.priority_orders) == 0:
                self.give_normal_orders(taxis, graph, search_algorithm)
            turn_barrier.wait()
        self.report_completion_time()

    def give_priority_orders(self, taxis: List[Taxi], graph: Graph, search_algorithm) -> bool:
        for order in self.priority_orders[:]:
            if self.give_order_to_best_taxi(taxis, graph, order, search_algorithm):
                self.priority_orders.remove(order)
        return len(self.priority_orders) == 0

    def give_normal_orders(self, taxis: List[Taxi], graph: Graph, search_algorithm) -> bool:
        normal_orders = [o for o in self.orders if o.getPriority() == 0 and o.status == Order_Status.Pendent.value]
        for order in normal_orders:
            if self.give_order_to_best_taxi(taxis, graph, order, search_algorithm):
                pass
        return len(normal_orders) == 0

    def update_terminated_orders(self):
        self.terminated_orders = [o for o in self.orders if o.isComplete()]

    def stop(self):
        self.running.clear()

    def report_completion_time(self):
        concluded_orders = [o for o in self.terminated_orders if o.completion_time > 0]
        if concluded_orders:
            for o in concluded_orders:
                print(f"Order ID: {o.id}, Completion Time: {o.completion_time}")
            avg = sum(o.completion_time for o in concluded_orders) / len(concluded_orders)
            print(f"Simulation stopped. Average completion time: {avg:.2f}")
        else:
            print("Simulation stopped. No orders were completed.")

