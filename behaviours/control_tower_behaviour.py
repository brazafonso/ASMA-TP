import asyncio
import time
import jsonpickle
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from objects.package import Package



class ControlTowerListener(CyclicBehaviour):
      '''Listener principal da torre de controlo'''
      async def run(self):
            # Get message
            msg = await self.receive(timeout=10)
            # If message and content are not None
            if msg:
                  print('Control Tower: ','Got message')
                  performative = msg.get_metadata('performative')
                  source = str(msg.sender)
                  if performative == 'request' and msg.body:
                        package:Package = jsonpickle.decode(msg.body)
                        type = package.message
                        if type == 'landing request':
                              print('Control Tower: ','Landing request received')
                              if len(self.agent.landing_queue) < self.get('max_queue'):
                                    self.agent.landing_queue.append((package.body,None))
                              # Fila de espera cheia, recusa aterragem
                              else:
                                    msg = Message(to=source)
                                    msg.set_metadata("performative", "refuse")
                                    await self.send(msg)

                  elif performative == 'inform' and msg.body:
                        package = jsonpickle.decode(msg.body)
                        type = package.message
                        # Gestor de gares informa que tem estacionamento disponivel
                        if type == 'available station':
                              print('Control Tower: ','Station available')
                              await self.landingHandler(msg)
                        # Aviao avisa que ja aterrou
                        elif type == 'landed':
                              jid = package.body
                              print('Control Tower: ',f'Plane {jid} landed')
                              # Tornar pista livre
                              self.get('airport_map').free_airstrip(plane_id=jid)
                        elif type == 'took off':
                              jid = package.body
                              print('Control Tower: ',f'Plane {jid} took off')
                              # Tornar pista livre
                              self.get('airport_map').free_airstrip(plane_id=jid)
                              await self.agent.stop()

                  elif performative == 'query-if' and msg.body:
                        package = jsonpickle.decode(msg.body)
                        type = package.message
                        # Gestor de gares procura uma pista para um aviao poder descolar
                        if type == 'takeoff request':
                              print('Control Tower: ','TakeOff request')
                              pos, plane = package.body
                              self.agent.take_off_queue.append((pos,plane,None))

      
      async def landingHandler(self,message):
            '''Trata dos passos finais da aterrisagem'''
            print('Control Tower: ','Taking care of landing procedure')
            package = jsonpickle.decode(message.body)
            airstrip,station,plane = package.body
            if self.get('airport_map').available_airstrip(airstrip.id):
                  self.agent.pop_landing_queue(plane.id)
                  # Reserva pista
                  self.get('airport_map').reserve_airstrip(airstrip.id,plane)

                  # Informa gestor de gares que pista ainda esta disponivel, para reservar gare
                  print('Control Tower: ','Reserving station')
                  package = Package('confirm pending arrival',station.id)
                  msg = Message(to=self.get('station_manager'))
                  msg.set_metadata("performative", "inform")
                  msg.body = jsonpickle.encode(package)
                  await self.send(msg)

                  # Informar aviao que pode aterrar
                  print('Control Tower: ',f'Confirming plane {plane.id} still alive')
                  package = Package('confirm landing',(airstrip,station))
                  msg = Message(to=str(plane.id))
                  msg.set_metadata("performative", "inform")
                  msg.body = jsonpickle.encode(package)
                  await self.send(msg)

                  # Esperar confirmacao do aviao
                  msg = await self.receive(timeout=5)

                  # Cancelar reservas se aviao nao responder
                  if not msg:
                        print('Control Tower: ','Plane not responding, canceling landing.')
                        self.get('airport_map').free_airstrip(id=airstrip.id)
                        package = Package('cancel arrival',station.id)
                        msg = Message(to=self.get('station_manager'))
                        msg.set_metadata("performative", "inform")
                        msg.body = jsonpickle.encode(package)
                        await self.send(msg)
                  else:
                        print('Control Tower: ','Landing happening')




      



class ControlTowerLandingRequester(CyclicBehaviour):
      '''Requester de pedidos de aterragem à gare'''

      async def run(self):
            print('Control Tower: ','Checking landing requests')
            if len(self.agent.landing_queue)>0:
                  plane,timestamp = self.agent.landing_queue[0]
                  current_time = time.time()
                  if not timestamp or timestamp < current_time - 10:
                        self.agent.landing_queue[0] = (plane,current_time)
                        available_airstrips = self.get('airport_map').available_airstrips()
                        if available_airstrips:
                              print('Control tower:','Sending requests to station manager')
                              package = Package('landing request',(available_airstrips,plane))
                              station_manager = self.get('station_manager')
                              if station_manager:
                                    msg = Message(to=self.get('station_manager'))
                                    msg.set_metadata("performative", "query-if")
                                    msg.body = jsonpickle.encode(package)

                                    await self.send(msg)
                                    print('Control tower:','landing request sent')
            # TODO: mudar para eventos
            await asyncio.sleep(2)


class ControlTowerTakeOffHandler(CyclicBehaviour):
      '''Handler de pedidos de descolagem'''

      async def run(self):
            print('Control Tower: ','Checking take off requests')
            if len(self.agent.take_off_queue)>0:
                  pos,plane,timestamp = self.agent.take_off_queue[0]
                  current_time = time.time()
                  if not timestamp or timestamp < current_time - 10:
                        print('Control tower:','Choosing airstrip for takeoff')
                        self.agent.take_off_queue[0] = (pos,plane,current_time)
                        airstrip = self.get('airport_map').closest_available_airstrip(pos)
                        # reserver pista, avisar gestor de gares e atualizar lista de espera para descolar
                        if airstrip:
                              print('Control tower:','Sending airstrip for takeoff')
                              self.agent.take_off_queue.pop(0)
                              self.get('airport_map').reserve_airstrip(airstrip.id,plane)
                              package = Package('available airstrip',(airstrip,plane.id))
                              station_manager = self.get('station_manager')
                              if station_manager:
                                    msg = Message(to=self.get('station_manager'))
                                    msg.set_metadata("performative", "inform")
                                    msg.body = jsonpickle.encode(package)

                                    await self.send(msg)
            # TODO: mudar para eventos
            await asyncio.sleep(2)



                  