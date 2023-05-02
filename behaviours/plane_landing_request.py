from spade.behaviour import OneShotBehaviour
from spade.message import Message
import jsonpickle

class PlaneLandingRequest(OneShotBehaviour):
        async def run(self):
            # Get message
            id = self.agent.get("id")
            # Create message
            msg = Message(to=self.agent.get("control_tower"))
            msg.body = jsonpickle.encode(id)
            msg.set_metadata("performative","request")
            msg.set_metadata("agent","plane")

            await self.send(msg)
                        