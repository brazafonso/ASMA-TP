import datetime
from spade import agent
from objects.flight import Flight
from objects.plane import Plane
from behaviours import plane_FMS_behaviour

class PlaneAgent(agent.Agent):

    async def setup(self):

        #Set Variables
        self.id_aviao = self.name
        self.estado = True
        self.nome_companhia = 'TAP'
        self.tipo = 'comercial' #'mercadorias'
        now = datetime.datetime.now()
        flight = Flight('Porto','Lisboa',now)

        self.plane = Plane(id=self.name,state=True,company='TAP',type='comercial',flight=flight)

        STATE_ONE = 'STATE_ONE'
        STATE_TWO = 'STATE_TWO'
        STATE_THREE = 'STATE_THREE'
        STATE_FOUR = 'STATE_FOUR'

        #Set Behaviors
        fsm = plane_FMS_behaviour.PlaneFSMBehaviour()
        fsm.add_state(name=STATE_ONE, state=plane_FMS_behaviour.PlaneRequestLandingBehaviour(), initial=True)
        fsm.add_state(name=STATE_TWO, state=plane_FMS_behaviour.PlaneListenLandingBehaviour()) 
        fsm.add_state(name=STATE_THREE, state=plane_FMS_behaviour.PlaneRequestTakeoffBehaviour())
        fsm.add_state(name=STATE_FOUR, state=plane_FMS_behaviour.PlaneListenTakeoffBehavior())
        fsm.add_transition(source=STATE_ONE,dest=STATE_TWO)
        fsm.add_transition(source=STATE_ONE,dest=STATE_THREE)
        fsm.add_transition(source=STATE_TWO,dest=STATE_THREE)
        fsm.add_transition(source=STATE_THREE,dest=STATE_FOUR)
        self.add_behaviour(fsm)


