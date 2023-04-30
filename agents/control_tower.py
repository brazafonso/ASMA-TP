from spade import agent
from objects.airport_map import AirportMap

class ControlTowerAgent(agent.Agent):

    
    # Agent setup
    async def setup(self):
        print(f'Control tower starting id : {self.jid}')
        self.set('landing_queue',[])
        self.set('take_off_queue',[])





    def status(self):
        '''Print o estado do aeroporto'''
        status = ''
        landing_queue = self.get('landing_queue')
        take_off_queue = self.get('take_off_queue')
        airport_map:AirportMap = self.get('airport_map') 

        status += '''
         _______________
        | Landing Queue |
            ---------
'''
        for plane in landing_queue:
            status += f'{str(plane)}\n'

        status += '''
         ________________
        | Take off Queue |
            ----------
'''
        for plane in take_off_queue:
            status += f'{str(plane)}\n'

        status += '''
         ___________
        | Airstrips |
           -------
'''
        for strip in airport_map.airstrips:
            status += f'{str(strip)}\n'

        status += '''
         __________
        | Stations |
            ----
'''
        for station in airport_map.stations:
            status += f'{str(station)}\n'
        return status