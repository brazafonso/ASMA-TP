from spade import agent
from behaviours.auction_manager_behaviour import *

import threading

class AuctionManagerAgent(agent.Agent):
    async def setup(self):
        self.write_log("AuctionManagerAgent started at {}".format(self.jid))

        # station.id : (station, Auction)
        self.stations = {}
        self.stations_lock = threading.Lock()

        # Populate stations
        stations_dict = self.get('airport_map').get_stations()
        for station_id in stations_dict:
            self.stations[station_id] = (stations_dict[station_id], None)

        self.airlines = {} # {airline.jid : airline}
        self.airlines_lock = threading.Lock()

        self.add_behaviour(AuctionManagerListenerBehaviour())
        self.add_behaviour(AuctionManagerUpdateAirlinesBehaviour(period=5))
        self.add_behaviour(AuctionManagerCleanerBehaviour(period=3))
        self.add_behaviour(AuctionManagerStatusSender(period=5))
        self.add_behaviour(AuctionManagerPaydayBehaviour(period=30))

    def write_log(self,message):
        '''Escreve os logs no ficheiro especificado, ou no stdout por default'''
        if self.get('logs'):
            self.get('logs_file').write(message+'\n')