import datetime
from spade.agent import Agent
from objects import Voo
from behaviours import AviaoFSMBehaviour

class Aviao:

    async def setup(self):

        #Set Variables
        self.id_aviao = Agent.name
        self.estado = True
        self.nome_companhia = 'TAP'
        self.tipo = 'comercial' #'mercadorias'
        data_agora = datetime.datetime.now()
        self.voo = Voo('Porto','Lisboa',data_agora)

        STATE_ONE = 'STATE_ONE'
        STATE_TWO = 'STATE_TWO'
        STATE_THREE = 'STATE_THREE'
        STATE_FOUR = 'STATE_FOUR'

        #Set Behaviors
        fsm = AviaoFSMBehaviour.AviaoFSMBehaviour()
        fsm.add_state(name=STATE_ONE, state=AviaoFSMBehaviour.AviaoRequestLandingBehaviour(), initial=True)
        fsm.add_state(name=STATE_TWO, state=AviaoFSMBehaviour.AviaoRequestLandingBehaviour()) 
        fsm.add_state(name=STATE_THREE, state=AviaoFSMBehaviour.AviaoRequestTakeoffBehaviour())
        fsm.add_state(name=STATE_FOUR, state=AviaoFSMBehaviour.AviaoListenLandingBehaviour())
        fsm.add_transition(source=STATE_ONE,dest=STATE_TWO)
        fsm.add_transition(source=STATE_ONE,dest=STATE_THREE)
        fsm.add_transition(source=STATE_TWO,dest=STATE_THREE)
        fsm.add_transition(source=STATE_THREE,dest=STATE_FOUR)
        self.add_behavior(fsm)


