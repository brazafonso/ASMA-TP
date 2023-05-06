import random
from spade.agent import Agent
from objects import airport_map
from behaviours.draw_airport_behaviour import DrawAirportBehaviour

class Dashboard_Manager(Agent):

    def setup(self):
        #Set Variables

        #Set Behaviors
        draw = DrawAirportBehaviour(period=2)
        self.add_behaviour(draw)