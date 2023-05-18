import threading

class Airline:
    '''Class to represent an airline'''

    def __init__(self, jid, name, type, budget, costs, profit_margin, strategy=None):
        self.jid = jid
        self.name = name
        self.type = type
        self.budget = budget
        self.costs = costs
        self.profit_margin = profit_margin
        self.strategy = strategy
        
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
        return Airline(self.jid, self.name, self.type, self.budget, self.costs, self.profit_margin)

    def update(self, airline):
        with self.lock:
            self.budget = airline.budget
    
    def payday(self):
        with self.lock:
            payday = self.budget * (self.profit_margin / 100)
            self.budget += payday

    def __str__(self):
        return "Airline: {} ({})".format(self.name, self.jid) + "\n" + \
                "Budget: {}".format(self.budget) + "\n" + \
                "Costs: {}".format(self.costs) + "\n" + \
                "Profit Margin: {}".format(self.profit_margin) + "\n" + \
                "Strategy: {}".format(self.strategy if self.strategy else "None")
    