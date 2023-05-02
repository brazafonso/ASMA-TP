import time
import jsonpickle
from spade.behaviour import CyclicBehaviour,OneShotBehaviour
from spade.message import Message
from objects.position import Position
from objects.package import Package



class ControlTowerListener(CyclicBehaviour):
        '''Listener principal da torre de controlo'''
        async def run(self):
            # Get message
            msg = await self.receive(timeout=10)

            print('got message')
            # If message and content are not None
            if msg:
                  performative = msg.get_metadata('performative')
                  source = str(msg.sender)
                  if performative == 'request' and msg.body:
                        package = jsonpickle.decode(msg.body)
                        type = package.message
                        if type == 'landing request':
                              self.agent.landing_queue.append(package.body)


class ControlTowerLandingRequester(CyclicBehaviour):
      '''Requester de pedidos de aterragem à gare'''

      async def run(self):
            print('Checking landing requests')
            if len(self.agent.landing_queue)>0:
                  plane = self.agent.landing_queue[0]
                  available_airstrips = self.get('airport_map').available_airstrips()
                  if available_airstrips:
                        print('Control tower:','sending requests to station manager')
                        # TODO: Penso que aqui apenas tenha de ser enviada uma pista, dado que é a torre que escolhe a pista
                        #       Na parte do station_manager vou já assumir que estou a receber uma pista
                        package = Package('landing request',(available_airstrips,plane))
                        station_manager = self.get('station_manager')
                        if station_manager:
                              msg = Message(to=self.get('station_manager'))
                              msg.set_metadata("performative", "query-if")
                              msg.body = jsonpickle.encode(package)

                              await self.send(msg)
                              print('Control tower:','landing request sent')
            else:
                  # TODO: mudar para eventos
                  time.sleep(2)




                        
                  