import time as tm

class Recharge_Station:
    def __init__(self, recharge_rate:float):
        self.recharge_rate = recharge_rate


    def charge(self, total_capacity:float, current_capacity:float):
        tm.sleep((total_capacity-current_capacity)/self.recharge_rate)
