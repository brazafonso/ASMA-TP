from spade import agent
from behaviours.station_manager_behaviour import *



class StationManagerAgent(agent.Agent):

    async def setup(self):
        print(f'Station manager starting id : {self.jid}')
        
        # "Station ID" : ("Airstrip ID", timestamp)
        self.pending_arrivals = {}

        # TODO: Periodically check if there are any old pending arrivals
        self.add_behaviour(StationManagerListener())
