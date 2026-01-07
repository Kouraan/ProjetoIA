import time
from threading import Thread, Barrier, Lock, Event, BrokenBarrierError
from typing import List

class Clock:

    def __init__(self, atualization_time:float = 0.5, turn_barrier:Barrier = None):
        self.time = 0
        self.day = 0
        self.hour = 0
        self.atualization_time = atualization_time
        self.turn_barrier = turn_barrier
        self.l = Lock()
        self.Running = Event()
        self.Running.set()

    def start_clock_task(self):
 
        while self.Running.is_set():
            try:
                for i in range(int(round(1/self.atualization_time))):
                    time.sleep(0.1)
                    self.turn_barrier.wait()

            except BrokenBarrierError:
                break

            self.time += 1

            if(self.time == 60):
                self.time = 0
                self.hour += 1
                if self.hour == 24:
                    self.hour = 0
                    self.day += 1 
        


    def get_clock_time(self): 
        with self.l:
            return self.hour
        
    
    def stop(self):
        self.Running.clear()
