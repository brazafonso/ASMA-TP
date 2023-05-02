from spade import agent
from behaviours.station_manager_behaviour import *



class StationManagerAgent(agent.Agent):

    async def setup(self):
        print(f'Station manager starting id : {self.jid}')

        self.add_behaviour(StationManagerListener())
