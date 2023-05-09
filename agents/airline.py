from spade import agent
from behaviours.airline_behaviour import *

import threading

class AirlineAgent(agent.Agent):

    async def setup(self, airline): # arguments passed on start()
        print("Airline Agent Setup")
        self.airline = airline
        self.airline.jid = self.jid

        self.available_stations = (True,[]) # (seen by bidding behaviour, [(auction_state, station)])
        self.available_stations_lock = threading.Lock()

        self.my_bids = {} # {station.id : bid}
        self.my_bids_lock = threading.Lock()

        self.add_behaviour(AirlineListenerBehaviour())
        self.add_behaviour(AirlineSubscribeToAuctionManager())
        self.add_behaviour(AirlineBiddingBehaviour(period=10)) # TODO: Adjust
