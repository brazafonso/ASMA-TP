from spade import agent
from behaviours.station_manager_behaviour import *



class StationManagerAgent(agent.Agent):

    async def setup(self):
        print(f'Station manager starting id : {self.jid}')
        
        # "Station ID" : ("Airstrip ID", timestamp)
        self.pending_arrivals = {}

        self.add_behaviour(StationManagerListener())
        self.add_behaviour(StationManagerClearOldReservationsBehaviour(period=1))
