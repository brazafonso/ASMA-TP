from spade import agent
from objects.airport_map import AirportMap
from behaviours.control_tower_behaviour import *

class ControlTowerAgent(agent.Agent):


    def __init__(self, jid: str, password: str, verify_security: bool = False,check_frequency:int= 2,min_request_handle_time:int=10):
         super().__init__(jid, password, verify_security)
         self.check_frequency = check_frequency
         self.min_request_handle_time = min_request_handle_time
    
    # Agent setup
    async def setup(self):
        self.write_log(f'Control tower starting id : {self.jid}')
        self.landing_queue = []
        self.take_off_queue = []
        self.add_behaviour(ControlTowerListener())
        self.add_behaviour(ControlTowerRequestsHandler(period=self.check_frequency))



    def pop_landing_queue(self,plane_id):
            '''Remove o aviao da queue de aterragem'''
            for i,plane in enumerate(self.landing_queue):
                  if plane.id == plane_id:
                        self.landing_queue.pop(i)
                        break

    def status(self):
        '''Print o estado do aeroporto'''
        status = ''
        landing_queue = self.landing_queue
        take_off_queue = self.take_off_queue
        airstrips = self.get('airport_map').get_airstrips()
        stations = self.get('airport_map').get_stations() 

        status += '''
         _______________
        | Landing Queue |
            ---------
'''
        for plane in landing_queue:
            status += f'{plane.id}\n'

        status += '''
         ________________
        | Take off Queue |
            ----------
'''
        for _,plane,_ in take_off_queue:
            status += f'{plane.id}\n'

        status += '''
         ___________
        | Airstrips |
           -------
'''
        for strip in airstrips:
            status += f'{str(strip)}\n'

        status += '''
         __________
        | Stations |
            ----
'''
        for station in stations:
            status += f'{str(station)}\n'
        return status
    

    def write_log(self,message):
        '''Escreve os logs no ficheiro especificado, ou no stdout por default'''
        if self.get('logs'):
            self.get('logs_file').write(message+'\n')