from spade import agent
from behaviours.auction_manager_behaviour import *

import threading

class AuctionManagerAgent(agent.Agent):
    async def setup(self):
        print("Auction Agent Setup")

        # station.id : (station, Auction)
        self.stations = {} # TODO: Pass/Create list of initial stations
        self.stations_lock = threading.Lock()

        self.airlines = {} # {airline.jid : airline}
        self.airlines_lock = threading.Lock()

        self.notify_success_bid = [] # [(airline.jid, success, bid)]
        self.notify_success_bid_lock = threading.Lock()

        self.add_behaviour(AuctionManagerListenerBehaviour())
        self.add_behaviour(AuctionManagerUpdateAirlinesBehaviour(period=5)) # TODO: Adjust
        self.add_behaviour(AuctionManagerCleanerBehaviour(period=3)) # TODO: Adjust
        self.add_behaviour(AuctionManagerNotifyAirlines(period=1)) # TODO: Adjust

    def write_log(self,message):
        '''Escreve os logs no ficheiro especificado, ou no stdout por default'''
        if self.get('logs'):
            self.get('logs_file').write(message+'\n')