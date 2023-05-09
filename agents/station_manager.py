from spade import agent
from behaviours.station_manager_behaviour import *

import threading


class StationManagerAgent(agent.Agent):

    async def setup(self):
        print(f'Station manager starting id : {self.jid}')
        
        # "Station ID" : ("Airstrip ID", timestamp)
        self.pending_arrivals = {}
        self.pending_arrivals_lock = threading.Lock()

        self.add_behaviour(StationManagerListener())
        self.add_behaviour(StationManagerClearOldReservationsBehaviour(period=1))
        self.add_behaviour(StationManagerStatusSender(period=2))


    def write_log(self,message):
        '''Escreve os logs no ficheiro especificado, ou no stdout por default'''
        if self.get('logs'):
            self.get('logs_file').write(message+'\n')