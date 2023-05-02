from spade.agent import Agent
from objects import Maps
from behaviours import draw_airport_behaviour

class Gestor_de_Dashboards(Agent):

    def setup(self):
        #Set Variables
        self.mapa = Maps()

        #Set Behaviors
        draw = draw_airport_behaviour.DrawAirportBehaviour()
        self.add_behaviour(draw)