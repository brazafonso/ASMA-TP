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

start_time = datetime.datetime.now()

class PlaneFSMBehaviour(FSMBehaviour):

    async def on_start(self):
        print(f'{self.agent.name} começou o seu comportamento!')

    async def on_end(self):
        print(f'{self.agent.name} acabou o seu comportamento!')
        await self.agent.stop()

class PlaneRequestLandingBehaviour(State):

    async def run(self):
        print('Plane in PlaneRequestLandingBehaviour')
        #O agente Avião muda o estado de pedir para descolar se já estiver estacionado numa gare
        
        if not self.agent.plane.state:
            self.set_next_state(STATE_THREE)

        package = Package('landing request',self.agent.plane)
        msg = Message(to=self.get('control_tower'))
        msg.set_metadata("performative", "request")
        msg.body = jsonpickle.encode(package)
        
        await self.send(msg)
        
        print('Landing request sent')
        self.set_next_state(STATE_TWO)
        
class PlaneListenLandingBehaviour(State):

    async def run(self):
        print('Plane in PlaneListenLandingBehaviour')
        #TODO decidir/ajustar tempo de timeout
        msg = await self.receive(timeout=60)

        #TODO: Não sei bem onde começar este start_time

        if msg:

            performative = msg.get_metadata('performative')

            fromA = msg.sender()

            print(f'{self.agent.name} recebeu uma mensagem com a performativa \
                  {performative} do agente {fromA}')

            if fromA == self.get('control_tower'):
                
                if performative == 'inform':

                        pista, gare = jsonpickle.decode(msg.body)

                        package = jsonpickle.decode(msg.body)
                        
                        type = package.message
                        
                        if type == 'confirm landing':

                            pista, gare = package.body 

                            print(f'Permição consedida ao avião {self.agent.name} para aterrar \
                                na pista {pista.getId_pista()} e para estacionar na gare {gare.getId_gare()}')

                            time_now = datetime.datetime.now()

                            #TODO: Verificar tempo de inicio de converçações com a torre de controlo

                            while((time_now-start_time).seconds<20):

                                time_now = datetime.datetime.now()

                                time.sleep(0.5)

                            #TODO: Verificar o tempo passado na pista de aterragem
                            
                            time.sleep(3)
                            
                            #Envio de mensagem à torre de controlo para indicar o fim do uso da pista

                            package = Package('landed',self.agent.name)
                            msg = Message(to=self.get('control_tower'))
                            msg.set_metadata("performative", "inform")
                            msg.body = jsonpickle.encode(package)
                            
                            await self.send(msg)                            

                            #TODO: Preciso de ter informação sobre a distância do avião à gare para fazer isto dinâmico
                            
                            #TODO: Verificar tempo de viagem até à gare

                            time.sleep(5)

                            #TODO: Avisar a Gare? 

                            self.set_next_state(STATE_THREE)

                        else:

                            print(f'Tipo da mensagem {type} inesperada \
                            agente {self.agent.name} vai abandonar o aeroporto!')
                        
                            self.kill()      

                #TODO definir a performative de abandonar o aeroporto
                elif performative =='refuse':

                    print(f'Agente {self.agent.name} vai abandonar o aeroporto, porque \
                          recebeu uma mensagem com a performative refuse do aeroporto!')
                    
                    self.kill()
                
                else:
                    
                    print(f'Performative {performative} inesperada \
                          agente {self.agent.name} vai abandonar o aeroporto!')
                    
                    self.kill()
                
            else:

                print(f'Mensagem recibida do agente {fromA} ao tentar aterrar \
                      agente {self.agent.name} vai abandonar o aeroporto!')
                
                self.kill()

        else:

            print(f'O agente {self.agent.name} não recebeu mensagem de resposta da \
                  Torre de Controlo.')
            
            self.kill()
            

class PlaneRequestTakeoffBehaviour(State):

    async def run(self):
        print('Plane in PlaneRequestTakeoffBehaviour')

        #TODO faz mais sentido definir quando se cria o Avião mas depois não temos a 
        # certeza se passamos da data com as esperas que introduzimos. Pode ser dicutido

        offset = random.randint(30,60)
        data_agora = datetime.datetime.now()
        data_descolagem = data_agora + datetime.timedelta(seconds = offset)
        self.agent.flight.set_take_off_date(data_descolagem)

        while((data_descolagem-data_agora).seconds>1):
            data_agora = datetime.datetime.now()
            time.sleep(0.5)

        package = Package('takeoff request',self.agent.name)
        msg = Message(to=self.get('station_manager')) # assumindo que envias isto qnd querias o avião
        msg.set_metadata("performative", "request")
        msg.body = jsonpickle.encode(package)
                
        await self.send(msg)

        self.set_next_state(STATE_FOUR)


class PlaneListenTakeoffBehavior(State):

    async def run(self):
        print('Plane in PlaneListenTakeoffBehavior')
        msg = await self.receive()

        performative = msg.get_metadata('performative')

        fromA = msg.sender()

        print(f'{self.agent.name} recebou uma mensagem com a performativa \
                {performative} do agente {fromA}')

        if fromA == self.get('station_manager'):
            
            if performative == 'inform':

                package = jsonpickle.decode(msg.body)

                type = package.message
                    
                if type == 'available airstrip':

                    posicao = package.body

                    print(f'Permição consedida ao avião {self.agent.name} para descolar \
                        na pista localizada na posição X:{posicao[0]},Y:{posicao[1]}')

                    #TODO Preciso de saber distâncias para fazer o sleep dinâmico. Neste caso o station manager pode 
                    # mandar também a posição da gare

                    #TODO: Discutir tempos

                    #Tempo Gare -> Pista

                    time.sleep(5)

                    #Tempo Pista -> Ar

                    time.sleep(5)

                    package = Package('took off',self.agent.name)
                    msg = Message(to=self.get('control_tower'))
                    msg.set_metadata("performative", "inform")
                    msg.body = jsonpickle.encode(package)
                    
                    await self.send(msg)   
                    
                    self.kill()

                else:

                    print(f'Tipo da mensagem {type} inesperada \
                            agente {self.agent.name} vai abandonar o aeroporto!')
                    
                    self.kill()

            else:
                            
                print(f'Performative {performative} inesperada \
                    agente {self.agent.name} vai abandonar o aeroporto!')
                
                self.kill()
                    
        else:

            print(f'Mensagem recibida do agente {fromA} ao tentar aterrar \
                agente {self.agent.name} vai abandonar o aeroporto!')
            
            self.kill()  

