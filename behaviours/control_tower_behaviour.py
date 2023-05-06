import asyncio
import time
import jsonpickle
from spade.behaviour import CyclicBehaviour,OneShotBehaviour
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
                        #  Pedido de estado de aeroporto
                        elif type == 'airport status request':
                              print('Control Tower: ',f'Airport status request')
                              self.set('status_requester',source)
                              self.agent.add_behaviour(ControlTowerStatusSender())

                  elif performative == 'inform' and msg.body:
                        package = jsonpickle.decode(msg.body)
                        type = package.message
                        # Gestor de gares informa que tem estacionamento disponivel
                        if type == 'available station':
                              print('Control Tower: ','Station available')
                              self.set('landing_confirmation',msg)
                              self.agent.add_behaviour(ControlTowerLandingHandler())
                        # Aviao avisa que ja aterrou
                        elif type == 'landed':
                              jid = package.body
                              print('Control Tower: ',f'Plane {jid} landed')
                              # Tornar pista livre
                              self.get('airport_map').free_airstrip(plane_id=jid)
                        # Pedido para descolagem
                        elif type == 'took off':
                              jid = package.body
                              print('Control Tower: ',f'Plane {jid} took off')
                              # Tornar pista livre
                              self.get('airport_map').free_airstrip(plane_id=jid)
                              # TODO: apenas para teste
                              await self.agent.stop()
                        # Pedido de estado do aeroporto
                        elif type == 'station status report':
                              print('Control Tower: ',f'Stations status report')
                              self.set('stations_status',package)
                              self.agent.add_behaviour(ControlTowerStationStatusHandler())
                        # Desistencia de aterragem
                        elif type == 'give up landing':
                              print('Control Tower: ',f'Plane gave up landing')
                              plane = package.body
                              self.agent.pop_landing_queue(plane.id)
                              package = Package('cancel arrival',plane)
                              msg = Message(to=self.get('station_manager'))
                              msg.set_metadata("performative", "inform")
                              msg.body = jsonpickle.encode(package)
                              await self.send(msg)


                  elif performative == 'query-if' and msg.body:
                        package = jsonpickle.decode(msg.body)
                        type = package.message
                        # Gestor de gares procura uma pista para um aviao poder descolar
                        if type == 'takeoff request':
                              print('Control Tower: ','TakeOff request')
                              pos, plane = package.body
                              self.agent.take_off_queue.append((pos,plane,None))


class ControlTowerLandingHandler(OneShotBehaviour):
      '''Trata dos passos finais da aterragem'''

      async def run(self):
            print('Control Tower: ','Taking care of landing procedure')
            message = self.get('landing_confirmation')
            package = jsonpickle.decode(message.body)
            airstrip,station,plane = package.body
            
            waiting = False

            for p,_ in self.agent.landing_queue:
                  if plane.id == p.id:
                        waiting = True 
                        break
            
            if waiting:
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
            # avisar gestor de gares que aviao ja nao quer aterrar
            else:
                  print('Control Tower: ','Plane has left landing queue.')
                  package = Package('cancel arrival',station.id)
                  msg = Message(to=self.get('station_manager'))
                  msg.set_metadata("performative", "inform")
                  msg.body = jsonpickle.encode(package)


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


class ControlTowerStatusSender(OneShotBehaviour):
      '''Enviar estado do aeroporto'''

      async def run(self):
            print('Control Tower: ','Sending airport status.')
            
            destination = self.get('status_requester')
            airport_map = self.get('airport_map')
            status = (airport_map.airstrips,airport_map.stations,self.agent.landing_queue,self.agent.take_off_queue)
            
            package = Package('airport status report',status)
            msg = Message(to=destination)
            msg.set_metadata("performative", "inform")
            msg.body = jsonpickle.encode(package)
            await self.send(msg)



class ControlTowerStationStatusHandler(OneShotBehaviour):
      '''Tratar de atualizar as gares no mapa'''

      async def run(self):
            print('Control Tower: ','Updating stations status.')
            
            status_package = self.get('stations_status')
            stations = status_package.body
            self.get('airport_map').update_stations(stations)










                  