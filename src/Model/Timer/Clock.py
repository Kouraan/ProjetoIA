import time
from threading import Thread, Barrier, Lock, Event, BrokenBarrierError
from typing import List

class Clock:

    def __init__(self, atualization_time:float = 1.0, turn_barrier:Barrier = None):
        self.time = 0  
        self.day = 0
        self.hour = 0
        self.minute = 0
        self.atualization_time = atualization_time
        self.turn_barrier = turn_barrier
        self.l = Lock()
        self.Running = Event()
        self.Running.set()

    def start_clock_task(self):
        while self.Running.is_set():
            try:
                time.sleep(self.atualization_time)
                self.turn_barrier.wait()

            except BrokenBarrierError:
                break

            self.time += 1
            self.minute += 1

            if self.minute == 60:
                self.minute = 0
                self.hour += 1
                if self.hour == 24:
                    self.hour = 0
                    self.day += 1
                    self.Running.clear() 
        

    def get_clock_minutes(self):
        with self.l:
            return self.day*1440 + self.hour*60 + self.minute

    def get_clock_time(self): 
        with self.l:
            return self.hour
        
    def get_Running(self):
        with self.l:
            return self.Running.is_set()
    
    def stop(self):
        with self.l:
            self.Running.clear()
    
    def get_traffic_changes(self):
        with self.l:
            if (self.hour == 6 or self.hour == 7):
                return 10

            if (self.hour == 9 or self.hour == 13):
                return 12
            
            if (self.hour >= 16 and self.hour <= 20):
                return 14
            
            return 2

            
