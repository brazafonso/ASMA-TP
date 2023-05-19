from spade import agent
from behaviours.airline_behaviour import *

import threading

class AirlineAgent(agent.Agent):

    def __init__(self, jid: str, password: str, airline, verify_security: bool = False):
        super().__init__(jid, password, verify_security)

        self.airline = airline

    async def setup(self): # arguments passed on start()
        self.write_log(f"AirlineAgent: Started with jid {self.jid}")

        self.subscribed = False

        self.available_stations = (True,[]) # (seen by bidding behaviour, [(auction_state, station)])
        self.available_stations_lock = threading.Lock()

        self.my_bids = {} # {station.id : bid}
        self.my_bids_lock = threading.Lock()

        self.add_behaviour(AirlineListenerBehaviour())
        self.add_behaviour(AirlineSubscribeToAuctionManager())
        self.add_behaviour(AirlineBiddingBehaviour(period=10))

    def write_log(self,message):
        '''Escreve os logs no ficheiro especificado, ou no stdout por default'''
        if self.get('logs'):
            self.get('logs_file').write(message+'\n')
