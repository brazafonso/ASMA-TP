import random
from spade.agent import Agent
from objects import airport_map
from behaviours import draw_airport_behaviour

class Gestor_de_Dashboards(Agent):

    def setup(self):
        #Set Variables
        id_map = random.randint(1,2)
        airport_name = f'/config/airport{id_map}.json'
        self.mapa = airport_map.AirportMap(airport_name)

        #Set Behaviors
        draw = draw_airport_behaviour.DrawAirportBehaviour()
        self.add_behaviour(draw)