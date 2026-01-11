import random
from src.Model.Graph.Edge import Edge
from src.Model.Timer.Clock import Clock
from threading import Barrier, Event, BrokenBarrierError

class Traffic_Manager:
    def __init__(self, edge_list: list[Edge]):
        self.edges = edge_list
        self.rng = random.Random(30)
        self.running = Event()

    def generate_congestions(self, clock: Clock):
        changes = clock.get_traffic_changes()
        changed_edges = list()
        for i in range(changes):
            edge: Edge = random.choice(self.edges)
            congestion_rate = random.random()
            edge.setCongestion(congestion_rate)
            if random.randint(1, 10) == 1:
                edge.set_Inactive()
            changed_edges.append(edge)
        return changed_edges

    def start_activity(self, barrier: Barrier, clock: Clock):
        self.running.set()
        old_time = -1
        changed_edges: list[Edge] = list()
        while self.running.is_set():  
            time = clock.get_clock_time()
            if old_time != time:
                for edge in changed_edges:
                    edge.reset_status()
                changed_edges = self.generate_congestions(clock)
                old_time = time
            try:
                barrier.wait()
            except BrokenBarrierError:
                break

    def stop(self):
        self.running.clear() 
