from spade.agent import Agent
from objects import Maps
from behaviours import DrawAirportBehaviour

class Gestor_de_Dashboards(Agent):

    def setup(self):
        #Set Variables
        self.mapa = Maps()

        #Set Behaviors
        draw = DrawAirportBehaviour.DrawAirportBehaviour()
        self.add_behaviour(draw)