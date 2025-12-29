import time
from threading import Thread, Barrier, Lock
from typing import List

class Clock:

    def __init__(self, atualization_time:float = 20, turn_barrier:Barrier = None):
        self.time = 0
        self.day = 0
        self.atualization_time = atualization_time
        self.turn_barrier = turn_barrier
        self.l = Lock()

    def start_clock_task(self):
 
        while True:
            self.turn_barrier.wait()
            self.time += 1

            if(self.time == 24):
                self.time = 0
                self.day += 1
        
    def get_clock_time(self): 
        with self.l:
            return self.time
