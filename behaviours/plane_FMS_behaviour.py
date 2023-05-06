import asyncio
import jsonpickle
import random
import time
import datetime
from objects.package import Package
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message

STATE_ONE = 'STATE_ONE'
STATE_TWO = 'STATE_TWO'
STATE_THREE = 'STATE_THREE'
STATE_FOUR = 'STATE_FOUR'

#TODO: Não sei bem onde começar este start_time
start_time = datetime.datetime.now()

class PlaneFSMBehaviour(FSMBehaviour):

    async def on_start(self):
        self.agent.write_log(f'{self.agent.name} começou o seu comportamento!')

    async def on_end(self):
        self.agent.write_log(f'{self.agent.name} acabou o seu comportamento!')
        await self.agent.stop()

class PlaneRequestLandingBehaviour(State):

    async def run(self):
        self.agent.write_log('Plane in PlaneRequestLandingBehaviour')
        #O agente Avião muda o estado de pedir para descolar se já estiver estacionado numa gare
        self.agent.write_log(f'Plane State {self.agent.plane.state}')
        if not self.agent.plane.state:
            self.set_next_state(STATE_THREE)

        package = Package('landing request',self.agent.plane)
        msg = Message(to=self.get('control_tower'))
        msg.set_metadata("performative", "request")
        msg.body = jsonpickle.encode(package)
        
        await self.send(msg)
        
        self.agent.write_log('Landing request sent')
        self.set_next_state(STATE_TWO)
        
class PlaneListenLandingBehaviour(State):

    async def run(self):
        self.agent.write_log('Plane in PlaneListenLandingBehaviour')
        #TODO decidir/ajustar tempo de timeout
        msg = await self.receive(timeout=60)

        if msg:
            performative = msg.get_metadata('performative')

            fromA = msg.sender

            self.agent.write_log(f'{self.agent.name} recebeu uma mensagem com a performativa \
                  {performative} do agente {fromA}')

            if str(fromA) == self.get('control_tower'):
                if performative == 'inform':

                        package = jsonpickle.decode(msg.body)

                        type = package.message
                        
                        if type == 'confirm landing':
                            pista, gare = package.body
                            
                            # Confirmar à torre de controlo que ainda esta a espera
                            package = Package('still waiting',self.agent.jid)
                            msg = Message(to=self.get('control_tower'))
                            msg.set_metadata("performative", "inform")
                            msg.body = jsonpickle.encode(package)
                            
                            await self.send(msg)


                            self.agent.write_log(f'Permição consedida ao avião {self.agent.name} para aterrar \
                                na pista {pista.id} e para estacionar na gare {gare.id}')

                            time_now = datetime.datetime.now()

                            #TODO: Verificar tempo de inicio de converçações com a torre de controlo
                            self.agent.write_log('Plane: Landing')
                            while((time_now-start_time).seconds<20):

                                time_now = datetime.datetime.now()

                                await asyncio.sleep(0.5)

                            #TODO: Verificar o tempo passado na pista de aterragem
                            
                            await asyncio.sleep(3)
                            
                            #Envio de mensagem à torre de controlo para indicar o fim do uso da pista

                            package = Package('landed',self.agent.jid)
                            msg = Message(to=self.get('control_tower'))
                            msg.set_metadata("performative", "inform")
                            msg.body = jsonpickle.encode(package)
                            
                            await self.send(msg)                            

                            #TODO: Preciso de ter informação sobre a distância do avião à gare para fazer isto dinâmico
                            
                            #TODO: Verificar tempo de viagem até à gare

                            await asyncio.sleep(5)

                            #TODO: Avisar a Gare? 

                            self.set_next_state(STATE_THREE)

                        else:

                            self.agent.write_log(f'Tipo da mensagem {type} inesperada \
                            agente {self.agent.jid} vai abandonar o aeroporto!')
                        
                            self.kill()      

                #TODO definir a performative de abandonar o aeroporto
                elif performative =='refuse':

                    self.agent.write_log(f'Agente {self.agent.jid} vai abandonar o aeroporto, porque \
                          recebeu uma mensagem com a performative refuse do aeroporto!')
                    
                    self.kill()
                
                else:
                    
                    self.agent.write_log(f'Performative {performative} inesperada \
                          agente {self.agent.jid} vai abandonar o aeroporto!')
                    
                    self.kill()
                
            else:

                self.agent.write_log(f'Mensagem recibida do agente {fromA} ao tentar aterrar \
                      agente {self.agent.jid} vai abandonar o aeroporto!')
                
                self.kill()

        else:
            
            self.agent.write_log(f'O agente {self.agent.jid} não recebeu mensagem de resposta da \
                  Torre de Controlo.')
            package = Package('give up landing',self.agent.plane)
            msg = Message(to=self.get('control_tower'))
            msg.set_metadata("performative", "inform")
            msg.body = jsonpickle.encode(package)
            await self.send(msg)
            
            self.kill()
            

class PlaneRequestTakeoffBehaviour(State):

    async def run(self):
        self.agent.write_log('Plane in PlaneRequestTakeoffBehaviour')

        #TODO faz mais sentido definir quando se cria o Avião mas depois não temos a 
        # certeza se passamos da data com as esperas que introduzimos. Pode ser dicutido

        offset = random.randint(1,10)
        data_agora = datetime.datetime.now()
        data_descolagem = data_agora + datetime.timedelta(seconds = offset)
        self.agent.plane.flight.set_take_off_date(data_descolagem)

        self.agent.write_log(f'Plane: waiting for {(data_descolagem-data_agora).seconds} seconds')

        while((data_descolagem-data_agora).seconds>1):
            data_agora = datetime.datetime.now()
            await asyncio.sleep(0.5)

        package = Package('takeoff request',self.agent.jid)
        msg = Message(to=self.get('station_manager')) # assumindo que envias isto qnd querias o avião
        msg.set_metadata("performative", "request")
        msg.body = jsonpickle.encode(package)
                
        await self.send(msg)

        self.set_next_state(STATE_FOUR)


class PlaneListenTakeoffBehavior(State):

    async def run(self):
        self.agent.write_log('Plane in PlaneListenTakeoffBehavior')
        msg = await self.receive(timeout=60)

        if msg:
            performative = msg.get_metadata('performative')

            fromA = msg.sender

            self.agent.write_log(f'{self.agent.name} recebou uma mensagem com a performativa \
                    {performative} do agente {fromA}')

            if str(fromA) == self.get('station_manager'):
                
                if performative == 'inform':

                    package = jsonpickle.decode(msg.body)

                    type = package.message
                        
                    if type == 'available airstrip':

                        pista = package.body

                        self.agent.write_log(f'Permição consedida ao avião {self.agent.jid} para descolar \
                            na pista localizada na posição X:{pista.pos.x},Y:{pista.pos.y}')

                        #TODO Preciso de saber distâncias para fazer o sleep dinâmico. Neste caso o station manager pode 
                        # mandar também a posição da gare

                        #TODO: Discutir tempos

                        #Tempo Gare -> Pista

                        await asyncio.sleep(5)

                        #Tempo Pista -> Ar

                        await asyncio.sleep(5)

                        package = Package('took off',self.agent.jid)
                        msg = Message(to=self.get('control_tower'))
                        msg.set_metadata("performative", "inform")
                        msg.body = jsonpickle.encode(package)
                        
                        await self.send(msg)   
                        
                        self.kill()

                    else:

                        self.agent.write_log(f'Tipo da mensagem {type} inesperada \
                                agente {self.agent.jid} vai abandonar o aeroporto!')
                        
                        self.kill()

                else:
                                
                    self.agent.write_log(f'Performative {performative} inesperada \
                        agente {self.agent.jid} vai abandonar o aeroporto!')
                    
                    self.kill()
                        
            else:

                self.agent.write_log(f'Mensagem recibida do agente {fromA} ao tentar levantar \
                    agente {self.agent.jid} vai abandonar o aeroporto!')
                
                self.kill()
        else:

            self.agent.write_log(f'O agente {self.agent.jid} não recebeu mensagem de resposta do \
                  Gestor de Gares.')
            self.set_next_state(STATE_THREE)


