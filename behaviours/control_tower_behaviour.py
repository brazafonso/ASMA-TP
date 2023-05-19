import asyncio
import random
import time
import jsonpickle
from spade.behaviour import CyclicBehaviour,OneShotBehaviour,PeriodicBehaviour
from spade.message import Message
from objects.package import Package


class ControlTowerListener(CyclicBehaviour):
      '''Listener principal da torre de controlo'''
      async def run(self):
            # Get message
            msg = await self.receive(timeout=10)
            # If message and content are not None
            if msg:
                  self.agent.write_log('Control Tower: Got message')
                  performative = msg.get_metadata('performative')
                  source = str(msg.sender)
                  if performative == 'request' and msg.body:
                        package:Package = jsonpickle.decode(msg.body)
                        type = package.message
                        if type == 'landing request':
                              self.agent.write_log('Control Tower: Landing request received')
                              if len(self.agent.landing_queue) < self.get('max_queue'):
                                    self.agent.landing_queue.append((package.body,None))
                              # Fila de espera cheia, recusa aterragem
                              else:
                                    msg = Message(to=source)
                                    msg.set_metadata("performative", "refuse")
                                    await self.send(msg)
                        #  Pedido de estado de aeroporto
                        elif type == 'airport status request':
                              self.agent.write_log('Control Tower: Airport status request')
                              self.set('status_requester',source)
                              self.agent.add_behaviour(ControlTowerStatusSender())

                  elif performative == 'inform' and msg.body:
                        package = jsonpickle.decode(msg.body)
                        type = package.message
                        # Gestor de gares informa que tem estacionamento disponivel
                        if type == 'available station':
                              self.agent.write_log('Control Tower: Station available')
                              self.set('landing_confirmation',msg)
                              self.agent.add_behaviour(ControlTowerLandingHandler())
                        # Aviao avisa que ja aterrou
                        elif type == 'landed':
                              jid = package.body
                              self.agent.write_log(f'Control Tower: Plane {jid} landed')
                              # Tornar pista livre
                              self.get('airport_map').free_airstrip(plane_id=jid)
                        # Pedido para descolagem
                        elif type == 'took off':
                              jid = package.body
                              self.agent.write_log(f'Control Tower: Plane {jid} took off')
                              # Tornar pista livre
                              self.get('airport_map').free_airstrip(plane_id=jid)
                              # atualizar numero de avioes restantes
                              n_planes = self.get('n_planes')
                              self.set('n_planes',n_planes - 1)
                              self.agent.write_log(f'Control Tower: Plane dealt with')
                        # Pedido de estado do aeroporto
                        elif type == 'station status report':
                              self.agent.write_log('Control Tower: Stations status report')
                              self.set('stations_status',package)
                              self.agent.add_behaviour(ControlTowerStationStatusHandler())
                        # Desistencia de aterragem
                        elif type == 'give up landing':
                              self.agent.write_log('Control Tower: Plane gave up landing')
                              plane = package.body
                              self.agent.pop_landing_queue(plane.id)
                              package = Package('cancel arrival',plane)
                              msg = Message(to=self.get('station_manager'))
                              msg.set_metadata("performative", "inform")
                              msg.body = jsonpickle.encode(package)
                              await self.send(msg)
                              # atualizar numero de avioes restantes
                              n_planes = self.get('n_planes')
                              self.set('n_planes',n_planes - 1) 
                              self.agent.write_log(f'Control Tower: Plane dealt with')


                  elif performative == 'query-if' and msg.body:
                        package = jsonpickle.decode(msg.body)
                        type = package.message
                        # Gestor de gares procura uma pista para um aviao poder descolar
                        if type == 'takeoff request':
                              self.agent.write_log('Control Tower: TakeOff request')
                              pos, plane = package.body
                              self.agent.take_off_queue.append((pos,plane,None))

            # Se ja tiverem sido tratados todos os avioes, encerra graciosamente
            if self.get('n_planes') == 0:
                  print('Ending')
                  self.agent.write_log('Control Tower: Work Done.')
                  await self.agent.stop()


class ControlTowerLandingHandler(OneShotBehaviour):
      '''Trata dos passos finais da aterragem'''

      async def run(self):
            self.agent.write_log('Control Tower: Taking care of landing procedure')
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
                        self.agent.write_log('Control Tower: Reserving station')
                        package = Package('confirm pending arrival',station.id)
                        msg = Message(to=self.get('station_manager'))
                        msg.set_metadata("performative", "inform")
                        msg.body = jsonpickle.encode(package)
                        await self.send(msg)


                        # Informar aviao que pode aterrar
                        self.agent.write_log(f'Control Tower: Confirming plane {plane.id} still alive')
                        package = Package('confirm landing',(airstrip,station))
                        msg = Message(to=str(plane.id))
                        msg.set_metadata("performative", "inform")
                        msg.body = jsonpickle.encode(package)
                        await self.send(msg)

                        # Esperar confirmacao do aviao
                        msg = await self.receive(timeout=5)

                        # Cancelar reservas se aviao nao responder
                        if not msg:
                              self.agent.write_log('Control Tower: Plane not responding, canceling landing.')
                              self.get('airport_map').free_airstrip(id=airstrip.id)
                              package = Package('cancel arrival',station.id)
                              msg = Message(to=self.get('station_manager'))
                              msg.set_metadata("performative", "inform")
                              msg.body = jsonpickle.encode(package)
                              await self.send(msg)
                              # atualizar numero de avioes restantes
                              n_planes = self.get('n_planes')
                              self.set('n_planes',n_planes - 1) 
                              self.agent.write_log(f'Control Tower: Plane dealt with')
                        else:
                              self.agent.write_log('Control Tower: Landing happening')
            # avisar gestor de gares que aviao ja nao quer aterrar
            else:
                  self.agent.write_log('Control Tower: Plane has left landing queue.')
                  package = Package('cancel arrival',station.id)
                  msg = Message(to=self.get('station_manager'))
                  msg.set_metadata("performative", "inform")
                  msg.body = jsonpickle.encode(package)


class ControlTowerRequestsHandler(PeriodicBehaviour):
      '''Handler de pedidos de aterragem e descolagem, priorizando pedidos de aterragem'''

      async def run(self):
            self.agent.write_log('Control Tower: Checking requests')
            min_time = self.agent.min_request_handle_time

            type_chance = random.randint(0,9)
            choice = None

            # Tratar de pedidos de aterragem (70% de probabilidade de ter prioridade)
            if type_chance > 2:
                  i,plane,timestamp = await self.choose_landing_request()
                  if plane:
                        current_time = time.time()
                        # verifica se o pedido nunca foi tratado ou ja passou mais de 10 segundos desde ultima vez
                        if not timestamp or timestamp < current_time - min_time:
                              choice = plane
                              self.agent.landing_queue[i] = (plane,current_time)
                              available_airstrips = self.get('airport_map').available_airstrips()
                              if available_airstrips:
                                    self.agent.write_log('Control tower:Sending requests to station manager')
                                    package = Package('landing request',(available_airstrips,plane))
                                    station_manager = self.get('station_manager')
                                    msg = Message(to=self.get('station_manager'))
                                    msg.set_metadata("performative", "query-if")
                                    msg.body = jsonpickle.encode(package)

                                    await self.send(msg)
                                    self.agent.write_log('Control tower:landing request sent')

            # Tratar de pedidos de descolagem
            elif not choice and len(self.agent.take_off_queue)>0:
                  i,pos,plane,timestamp = await self.choose_take_off_request()
                  current_time = time.time()
                  # verifica se o pedido nunca foi tratado ou ja passou mais de 10 segundos desde ultima vez
                  if not timestamp or timestamp < current_time - min_time:
                        self.agent.write_log('Control tower: Choosing airstrip for takeoff')
                        self.agent.take_off_queue[i] = (pos,plane,current_time)
                        airstrip = self.get('airport_map').closest_available_airstrip(pos)
                        # reserver pista, avisar gestor de gares e atualizar lista de espera para descolar
                        if airstrip:
                              self.agent.write_log('Control tower: Sending airstrip for takeoff')
                              self.agent.take_off_queue.pop(i)
                              self.get('airport_map').reserve_airstrip(airstrip.id,plane)
                              package = Package('available airstrip',(airstrip,plane.id))
                              station_manager = self.get('station_manager')
                              if station_manager:
                                    msg = Message(to=self.get('station_manager'))
                                    msg.set_metadata("performative", "inform")
                                    msg.body = jsonpickle.encode(package)

                                    await self.send(msg)

            

      async def choose_take_off_request(self):
            '''Escolhe o pedido de descolagem mais urgente para tratar'''
            # (i,pos,plane, timestamp)
            chosen = (0,None,None,None)
            for i,(pos,plane,timestamp) in enumerate(self.agent.take_off_queue):
                  # iniciar
                  if not chosen[1]:
                        chosen = (i,pos,plane,timestamp)
                  else:
                        # escolher aviao com timestamp mais antiga
                        if chosen[2] and timestamp:
                              if timestamp and timestamp > chosen[2]:
                                    chosen = (i,pos,plane,timestamp)
                        elif timestamp:
                              chosen = (i,pos,plane,timestamp)
            return chosen
      
      
      async def choose_landing_request(self):
            '''Escolhe o pedido de aterragem mais urgente para tratar'''
            # (i,plane, timestamp)
            chosen = (0,None,None)
            for i, (plane,timestamp) in enumerate(self.agent.landing_queue):
                  # iniciar
                  if not chosen[1]:
                        chosen = (i,plane,timestamp)
                  else:
                        # escolher aviao com timestamp mais antiga
                        if chosen[2] and timestamp:
                              if timestamp and timestamp > chosen[2]:
                                    chosen = (i,plane,timestamp)
                        elif timestamp:
                              chosen = (i,plane,timestamp)
            return chosen




class ControlTowerStatusSender(OneShotBehaviour):
      '''Enviar estado do aeroporto'''

      async def run(self):
            self.agent.write_log('Control Tower: Sending airport status.')
            
            destination = self.get('status_requester')
            airstrips = self.get('airport_map').get_airstrips()
            stations = self.get('airport_map').get_stations()
            status = (airstrips,stations,self.agent.landing_queue,self.agent.take_off_queue)
            
            package = Package('airport status report',status)
            msg = Message(to=destination)
            msg.set_metadata("performative", "inform")
            msg.body = jsonpickle.encode(package)
            await self.send(msg)
            self.agent.write_log(self.agent.status())



class ControlTowerStationStatusHandler(OneShotBehaviour):
      '''Tratar de atualizar as gares no mapa'''

      async def run(self):
            self.agent.write_log('Control Tower: Updating stations status.')
            
            status_package = self.get('stations_status')
            stations = status_package.body
            self.get('airport_map').update_stations(stations)










                  