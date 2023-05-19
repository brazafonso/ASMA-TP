import asyncio
import jsonpickle
import random
import math
import datetime
from objects.package import Package
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message

STATE_ONE = 'STATE_ONE'
STATE_TWO = 'STATE_TWO'
STATE_THREE = 'STATE_THREE'
STATE_FOUR = 'STATE_FOUR'

start_time = datetime.datetime.now()

class PlaneFSMBehaviour(FSMBehaviour):

    async def on_start(self):
        self.agent.write_log(f'{self.agent.name}: Started it\'s behaviour!')

    async def on_end(self):
        self.agent.write_log(f'{self.agent.name}: Finished it\'s behaviour!')
        await self.agent.stop()

class PlaneRequestLandingBehaviour(State):

    async def run(self):
        self.agent.write_log(f'{self.agent.name}: In PlaneRequestLandingBehaviour')

        #O agente Avião muda o estado de pedir para descolar se já estiver estacionado numa gare

        self.agent.write_log(f'{self.agent.name}: State {self.agent.plane.state}')
        if not self.agent.plane.state:
            self.set_next_state(STATE_THREE)
        else:
            package = Package('landing request',self.agent.plane)
            msg = Message(to=self.get('control_tower'))
            msg.set_metadata("performative", "request")
            msg.body = jsonpickle.encode(package)
            
            await self.send(msg)
            
            self.agent.write_log(f'{self.agent.name}: Landing request sent')
            self.set_next_state(STATE_TWO)
        
class PlaneListenLandingBehaviour(State):

    async def run(self):
        self.agent.write_log(f'{self.agent.name}: In PlaneListenLandingBehaviour')
        
        msg = await self.receive(timeout=self.agent.max_wait_landing)

        if msg:
            performative = msg.get_metadata('performative')

            fromA = msg.sender
            
            self.agent.write_log(f'{self.agent.name}: Recived message with the performative {performative} from {fromA}')

            if str(fromA) == self.get('control_tower'):
                if performative == 'inform':

                        package = jsonpickle.decode(msg.body)

                        type = package.message
                        
                        if type == 'confirm landing':
                            airstrip, station = package.body
                            
                            # Confirmar à torre de controlo que ainda esta a espera

                            package = Package('still waiting',self.agent.jid)
                            msg = Message(to=self.get('control_tower'))
                            msg.set_metadata("performative", "inform")
                            msg.body = jsonpickle.encode(package)
                            
                            await self.send(msg)

                            self.agent.write_log(f'{self.agent.name}: Permission granted to land in airstrip {airstrip.id} and go to station {station.id}')

                            time_now = datetime.datetime.now()

                            while((time_now-start_time).seconds<20):

                                time_now = datetime.datetime.now()

                                await asyncio.sleep(0.5)

                            #Tempo Ar -> Pista


                            speed = self.agent.plane_speed

                            distance = airstrip.get_pos_x()

                            time = distance / speed
                            
                            await asyncio.sleep(time)
                            
                            #Envio de mensagem à torre de controlo para indicar o fim do uso da pista

                            package = Package('landed',self.agent.jid)
                            msg = Message(to=self.get('control_tower'))
                            msg.set_metadata("performative", "inform")
                            msg.body = jsonpickle.encode(package)
                            
                            await self.send(msg) 

                            #Tempo Pista -> Gare                           

                            airstrip_pos = (airstrip.get_pos_x(),airstrip.get_pos_y())

                            station_pos = (station.get_pos_x(),station.get_pos_y())

                            distance_airstirp_station = math.sqrt(math.pow((station_pos[0]-airstrip_pos[0]),2) + math.pow((station_pos[1]-airstrip_pos[1]),2))

                            park_time = distance_airstirp_station / speed
                            
                            await asyncio.sleep(park_time)

                            self.set_next_state(STATE_THREE)

                        else:

                            self.agent.write_log(f'{self.agent.name}: Unexpected message type {type}. {self.agent.name} will leave airport!')
                        
                            self.kill()      

                elif performative =='refuse':

                    self.agent.write_log(f'{self.agent.name}: Recived a message with performative \'refuse\' from Control Tower. {self.agent.name} will leave airport!')
                    
                    self.kill()
                
                else:
                    
                    self.agent.write_log(f'{self.agent.name}: Unexpected performative {performative}. {self.agent.name} will leave airport!')
                    
                    self.kill()
                
            else:

                self.agent.write_log(f'{self.agent.name}: Unexpected mensage from agent {fromA} while landing. {self.agent.name} will leave airport!')
                
                self.kill()

        else:
            
            self.agent.write_log(f'{self.agent.name}: Timeout reached in waiting for a response from Control Tower while in landing State. {self.agent.name} will leave airport!')
            package = Package('give up landing',self.agent.plane)
            msg = Message(to=self.get('control_tower'))
            msg.set_metadata("performative", "inform")
            msg.body = jsonpickle.encode(package)
            await self.send(msg)
            
            self.kill()
            

class PlaneRequestTakeoffBehaviour(State):

    async def run(self):
        self.agent.write_log(f'{self.agent.name}: In PlaneRequestTakeoffBehaviour')

        offset = random.randint(1,self.agent.max_wait_in_station)
        data_agora = datetime.datetime.now()
        data_descolagem = data_agora + datetime.timedelta(seconds = offset)
        self.agent.plane.flight.set_take_off_date(data_descolagem)

        self.agent.write_log(f'{self.agent.name}: Waiting for {(data_descolagem-data_agora).seconds} seconds until requesting takeoff!')

        while((data_descolagem-data_agora).seconds>1):
            data_agora = datetime.datetime.now()
            await asyncio.sleep(0.5)

        package = Package('takeoff request',self.agent.jid)
        msg = Message(to=self.get('station_manager'))
        msg.set_metadata("performative", "request")
        msg.body = jsonpickle.encode(package)
                
        await self.send(msg)

        self.set_next_state(STATE_FOUR)


class PlaneListenTakeoffBehavior(State):

    async def run(self):
        self.agent.write_log(f'{self.agent.name}: In PlaneListenTakeoffBehavior')
        msg = await self.receive(timeout=self.agent.max_wait_take_off)

        if msg:
            performative = msg.get_metadata('performative')

            fromA = msg.sender

            self.agent.write_log(f'{self.agent.name}: Recived message with the performative {performative} from {fromA}')

            if str(fromA) == self.get('station_manager'):
                
                if performative == 'inform':

                    package = jsonpickle.decode(msg.body)

                    type = package.message
                        
                    if type == 'available airstrip':

                        airstrip, station = package.body

                        self.agent.write_log(f'{self.agent.name}: Permission granted to takeoff in airstrip {airstrip.id} in position X:{airstrip.pos.x},Y:{airstrip.pos.y}')

                        #Tempo Gare -> Pista

                        speed = self.agent.plane_speed
                        
                        airstrip_pos = (airstrip.get_pos_x(),airstrip.get_pos_y())

                        station_pos = (station.get_pos_x(),station.get_pos_y())

                        distance_airstirp_station = math.sqrt(math.pow((station_pos[0]-airstrip_pos[0]),2) + math.pow((station_pos[1]-airstrip_pos[1]),2))

                        unpark_time = distance_airstirp_station / speed
                        self.agent.write_log(f'{self.agent.name}: Taking {unpark_time} seconds to reach the airstrip.')
                        await asyncio.sleep(unpark_time)

                        #Tempo Pista -> Ar

                        # Demora 7 segundos a aterrar com a velocidade default 10

                        distance = airstrip.get_pos_x()

                        time = distance / speed
                        
                        self.agent.write_log(f'{self.agent.name}: Taking {time} seconds to complete take off.')
                        await asyncio.sleep(time)

                        package = Package('took off',self.agent.jid)
                        msg = Message(to=self.get('control_tower'))
                        msg.set_metadata("performative", "inform")
                        msg.body = jsonpickle.encode(package)
                        
                        await self.send(msg)   
                        
                        self.kill()

                    else:

                        self.agent.write_log(f'{self.agent.name}: Unexpected message type {type}.  {self.agent.name} will leave airport!')
                        
                        self.kill()

                else:
                                
                    self.agent.write_log(f'{self.agent.name}: Unexpected performative {performative}. {self.agent.name} will leave airport!')
                    
                    self.kill()
                        
            else:

                self.agent.write_log(f'{self.agent.name}: Unexpected mensage from agent {fromA} while taking-off. {self.agent.name} will leave airport!')
                
                self.kill()
        else:

            self.agent.write_log(f'{self.agent.name}: Timeout reached in waiting for a response from Station Manager while in take-off State. {self.agent.name} will go back to State PlaneRequestTakeoffBehaviour!')
            self.set_next_state(STATE_FOUR)


