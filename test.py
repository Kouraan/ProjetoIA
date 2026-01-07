import random
from src.TaxiGreen import TaxiGreen

random.seed(42)
default_number_of_taxis = 5
default_search_algorithm = 3

taxi_green = TaxiGreen(default_number_of_taxis, default_search_algorithm, 0.5)
taxi_green.start_simulation()