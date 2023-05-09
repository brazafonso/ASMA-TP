# TODO: Needs to be used by the other objects

import threading

class Airline:
    '''Class to represent an airline'''

    def __init__(self, jid, name, type, budget, costs, strategy=None):
        self.jid = jid
        self.name = name
        self.type = type
        self.budget = budget
        self.costs = costs
        
        # Unwrap strategy
        if strategy:
            self.parallel_bids = strategy['parallel_bids']
            self.relative_max_bid = strategy['relative_max_bid']
            self.relative_max_increment = strategy['relative_max_increment']
        else:
            self.parallel_bids = -1
            self.relative_max_bid = -1
            self.relative_max_increment = -1
        
        self.lock = threading.Lock()
    
    def get_simple_object(self):
        return Airline(self.jid, self.name, self.type, self.budget)

    def update(self, airline):
        with self.lock:
            self.budget = airline.budget
