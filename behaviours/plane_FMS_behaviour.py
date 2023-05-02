import jsonpickle
import random
import time
import datetime
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message

STATE_ONE = 'STATE_ONE'
STATE_TWO = 'STATE_TWO'
STATE_THREE = 'STATE_THREE'
STATE_FOUR = 'STATE_FOUR'

class AviaoFSMBehaviour(FSMBehaviour):

    async def on_start(self):
        print(f'{self.agent.name} começou o seu comportamento!')

    async def on_end(self):
        print(f'{self.agent.name} acabou o seu comportamento!')
        await self.agent.stop()

class AviaoRequestLandingBehaviour(State):

    async def run(self):

        #O agente Avião muda o estado de pedir para descolar se já estiver estacionado numa gare
        if not(self.agent.estado):
            self.set_next_state(STATE_THREE)

        msg = Message(to=self.get('control_tower'))
        msg.set_metadata("performative", "request")
        msg.body = jsonpickle.encode(self.agent)
        
        await self.send(msg)

        self.set_next_state(STATE_TWO)
        
class AviaoListenLandingBehaviour(State):

    async def run(self):

        #TODO decidir/ajustar tempo de timeout
        msg = await self.receive(timeout=60)

        if msg:

            performative = msg.get_metadata('performative')

            fromA = msg.sender()

            print(f'{self.agent.name} recebeu uma mensagem com a performativa \
                  {performative} do agente {fromA}')

            if fromA == 'Torre_de_Controlo':
                
                if performative == 'inform':

                    pista, gare = jsonpickle.decode(msg.body)

                    #TODO Introduzir tempos de aterragem e deslacamento para a gare

                    print(f'Permição consedida ao avião {self.agent.name} para aterrar \
                          na pista {pista.getId_pista()} e para estacionar na gare {gare.getId_gare()}')
                    
                    self.set_next_state(STATE_THREE)

                #TODO definir a performative de espera no ar
                elif performative == 'wait':

                    msg1 = await self.receive()

                    performative1 = msg1.get_metadata('performative')

                    fromA1 = msg1.sender()

                    if fromA1 == 'Torre_de_Controlo':
                
                        if performative1 == 'inform':

                            pista, gare = jsonpickle.decode(msg.body)

                            print(f'Permição consedida ao avião {self.agent.name} para aterrar \
                                na pista {pista.getId_pista()} e para estacionar na gare {gare.getId_gare()}')
                            
                            self.set_next_state(STATE_THREE)

                        else:
                        
                            print(f'Performative {performative} inesperada \
                                agente {self.agent.name} vai abandonar o aeroporto!')
                            
                            self.kill()
                    
                    else:

                        print(f'Mensagem recibida do agente {fromA} ao tentar aterrar \
                            agente {self.agent.name} vai abandonar o aeroporto!')
                        
                        self.kill()       

                #TODO definir a performative de abandonar o aeroporto
                elif performative =='leave':

                    print(f'Agente {self.agent.name} vai abandonar o aeroporto, porque \
                          recebeu uma mensagem com a performative leave do aeroporto!')
                    
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
            

class AviaoRequestTakeoffBehaviour(State):

    async def run(self):


        #TODO faz mais sentido definir quando se cria o Avião mas depois não temos a 
        # certeza se passamos da data com as esperas que introduzimos. Pode ser dicutido

        offset = random.randint(30,60)
        data_agora = datetime.datetime.now()
        data_descolagem = data_agora + datetime.timedelta(seconds = offset)
        self.agent.voo.setData_descolagem(data_descolagem)

        while((data_agora.minute != data_descolagem.minute)or(data_agora.second != data_descolagem.second)):
            time.sleep(0.5)

        msg = Message(to='Gestor_de_Gares@alexandre-aspire-a515-52g')
        msg.set_metadata("performative", "request")
        msg.body = jsonpickle.encode(self.agent.name)
        
        await self.send(msg)

        self.set_next_state(STATE_FOUR)


class AviaoListenTakeoffBehavior(State):

    async def run(self):

        msg = await self.receive()

        performative = msg.get_metadata('performative')

        fromA = msg.sender()

        print(f'{self.agent.name} recebou uma mensagem com a performativa \
                {performative} do agente {fromA}')

        if fromA == 'Gestor_de_Gares':
            
            if performative == 'inform':

                posicao = jsonpickle.decode(msg.body)

                print(f'Permição consedida ao avião {self.agent.name} para descolar \
                      na pista localizada na posição X:{posicao[0]},Y:{posicao[1]}')
                
                #TODO introduzir tempos de deslocação da gare para a pista e para descolar
                
                self.kill()

            else:
                            
                print(f'Performative {performative} inesperada \
                    agente {self.agent.name} vai abandonar o aeroporto!')
                
                self.kill()
                    
        else:

            print(f'Mensagem recibida do agente {fromA} ao tentar aterrar \
                agente {self.agent.name} vai abandonar o aeroporto!')
            
            self.kill()  

