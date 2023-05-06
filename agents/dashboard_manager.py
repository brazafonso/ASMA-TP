import random
from spade.agent import Agent
from objects import airport_map
from behaviours.draw_airport_behaviour import DrawAirportBehaviour

class Dashboard_Manager(Agent):

    def __init__(self, jid: str, password: str, verify_security: bool = False,period:int=2):
        super().__init__(jid, password, verify_security)
        self.period = period




    async def setup(self):
        #Set Variables

        #Set Behaviors
        draw = DrawAirportBehaviour(period=self.period)
        self.add_behaviour(draw)


    def write_log(self,message):
        '''Escreve os logs no ficheiro especificado, ou no stdout por default'''
        if self.get('logs'):
            self.get('logs_file').write(message+'\n')