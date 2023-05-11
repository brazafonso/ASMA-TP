import datetime
from spade import agent
from objects.flight import Flight
from objects.plane import Plane
from behaviours import plane_FMS_behaviour

class PlaneAgent(agent.Agent):

    def __init__(self, jid: str, password: str, verify_security: bool = False,
                 state=True,airline_name=None,type:str='comercial',plane_speed:int=10,
                 max_wait_in_station:int=60,max_wait_landing:int=60,
                 max_wait_take_off:int=60,origin:str='Porto',destination:str='Lisboa'):
        
        super().__init__(jid, password, verify_security)
        self.state = state
        self.airline_name = airline_name
        self.type = type
        self.plane_speed = plane_speed
        self.max_wait_in_station = max_wait_in_station
        self.max_wait_landing = max_wait_landing
        self.max_wait_take_off = max_wait_take_off
        #Set Variables
        now = datetime.datetime.now()
        flight = Flight(origin,destination,now)

        self.plane = Plane(id=self.jid,state=self.state,airline_name=self.airline_name,type=self.type,flight=flight)

    async def setup(self):

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
        fsm.add_transition(source=STATE_FOUR,dest=STATE_THREE)
        self.add_behaviour(fsm)


    def write_log(self,message):
        '''Escreve os logs no ficheiro especificado, ou no stdout por default'''
        if self.get('logs'):
            self.get('logs_file').write(message+'\n')
