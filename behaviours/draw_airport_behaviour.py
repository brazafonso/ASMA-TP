import jsonpickle
from objects.package import Package
from spade.message import Message
from spade.behaviour import PeriodicBehaviour

class DrawAirportBehaviour(PeriodicBehaviour):
    '''Behaviour que trata de pedir informação à Torre de Controlo para depois a desenhar'''
    async def on_start(self):
        self.agent.get('airport_map').set_frame()
        self.agent.get('airport_map').place_airstrips()
        self.agent.get('airport_map').place_stations()
        self.agent.get('airport_map').place_roads()
    
    async def run(self):

        #Envio de mensagem à Torre de Controlo a pedir a informação de estado
        package = Package('airport status request',)
        msg = Message(to=self.get('control_tower'))
        msg.set_metadata("performative", "request")
        msg.body = jsonpickle.encode(package)

        await self.send(msg)

        msg = await self.receive(timeout=1)

        if msg:
            performative = msg.get_metadata('performative')
            if performative == 'inform':
                package = jsonpickle.decode(msg.body)

                type = package.message
                if type == 'airport status report':
                    self.agent.write_log('Dashboard: Updating and drawing map')
                    airstrips,stations,landing_queue,take_off_queue = package.body

                    self.agent.get('airport_map').map_update_airstrips(airstrips)
                    self.agent.get('airport_map').map_update_stations(stations)
                    self.agent.get('airport_map').update_landing_queue(landing_queue)
                    self.agent.get('airport_map').update_take_off_queue(take_off_queue)

                    self.agent.get('airport_map').draw_map()
                        
                else:
                    pass
                              
            else:
                pass

        else:
            pass