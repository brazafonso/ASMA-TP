from spade.behaviour import CyclicBehaviour
import jsonpickle
from objects.position import Position

class ControlTowerListener(CyclicBehaviour):
        async def run(self):
            # Get message
            msg = await self.receive(timeout=10)

            # If message and content are not None
            if msg:
                  performative = msg.get_metadata('performative')
                  source = str(msg.sender)
                  if performative == 'request' and msg.body:
                        obj = jsonpickle.decode(msg.body)
                        
                        
                  