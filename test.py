import threading
import random
from src.TaxiGreen import TaxiGreen

random.seed(42)
default_number_of_taxis = 5
default_search_algorithm = 3

taxi_green = TaxiGreen(default_number_of_taxis, default_search_algorithm, 0.05)

def stop_simulation():
    print("Stopping simulation!")
    taxi_green.stop()

stop_thread = threading.Timer(30.0, stop_simulation)
stop_thread.start()

taxi_green.start_simulation()

