import threading
import time

class Auction:
    """Auction for a station"""

    OPEN = 'open'
    CLOSED = 'closed'

    def __init__(self, base_value, station, logs, logs_file):
        self.base_value = base_value
        self.station = station
        self.end_time = time.time() + 30
        self.bids = []
        self.winning_bid = None
        self.state = Auction.OPEN
        self.logs = logs
        self.logs_file = logs_file

        # Create thread to handle auction and results
        # The thread must be run when the end_time is reached
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

        # Lock the bid list
        self.lock = threading.Lock()
    
    def is_over(self):
        return self.state == Auction.CLOSED
    
    def add_bid(self, bid):
        if not self.is_over():
            if bid.value >= self.base_value:
                with self.lock:
                    self.bids.append(bid)
                    return True
        return False
    
    def next_winner(self):
        if self.winning_bid:
            with self.lock:
                self.bids.remove(self.winning_bid)
                self.winning_bid = max(self.bids, key=lambda bid: bid.value)


    def run(self):
        self.write_log("Auction for station {} started.".format(self.station.id))

        # Sleep until end_time
        while time.time() < self.end_time:
            time.sleep(1)
        
        self.write_log("Auction for station {} ended. Choosing the winner...".format(self.station.id))

        # Choose the winner
        with self.lock:
            self.state = Auction.CLOSED
            if self.bids:
                self.winning_bid = max(self.bids, key=lambda bid: bid.value)    
                self.write_log("Auction for station {} ended. Winner: {}".format(self.station.id, self.winning_bid.station.id))
            else:
                self.write_log("Auction for station {} ended. No bids.".format(self.station.id))

    def write_log(self,message):
        '''Escreve os logs no ficheiro especificado, ou no stdout por default'''
        if self.logs:
            self.logs_file.write(message+'\n')
