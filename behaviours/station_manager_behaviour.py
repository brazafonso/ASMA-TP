from spade.behaviour import CyclicBehaviour
from spade.message import Message
from objects.package import Package

import jsonpickle

class StationManagerListener(CyclicBehaviour):
    '''Listener principal do station manager'''
    async def run(self):
        # Get message
        msg = await self.receive(timeout=10)
        
        # Possible messages:
        # - Query-if to check if station is available
        # - Request to leave station
        # - Inform to inform that airstrip is available (allow request to leave station)
        if msg:
            performative = msg.get_metadata('performative')
            if performative == 'query-if':
                # Check if station is available
                # If available, send inform
                # Update station state
                package = jsonpickle.decode(msg.body)
                type = package.message
                if type == 'landing request':
                    airstrip, plane = package.body

                    # Check closest station to airstrip
                    closest_station = None
                    min_distance = None
                    for station in self.get('airport_map').stations:
                        if station.state == 0 and station.type == plane.type:
                            if closest_station is None:
                                closest_station = station
                                min_distance = airstrip.pos.distance(station.pos)
                            else:
                                distance = airstrip.pos.distance(station.pos)
                                if distance < min_distance:
                                    closest_station = station
                                    min_distance = distance
                    
                    if closest_station is not None:
                        package = Package('available station',closest_station)
                        control_tower = self.get('control_tower')
                        if control_tower:
                            msg = Message(to=control_tower)
                            msg.set_metadata("performative", "inform")
                            msg.body = jsonpickle.encode(package)

                            await self.send(msg)
                            print('Station manager: available station sent!')

                            # Update station state
                            for station in self.get('airport_map').stations:
                                if station.id == closest_station.id:
                                    station.state = 1 # Occupied
                                    break

            elif performative == 'request':
                # Request to leave station
                # If everything OK, send query-if to control tower
                package = jsonpickle.decode(msg.body)
                type = package.message
                if type == 'takeoff request':
                    plane_jid = package.body
                    # Check if plane is in station
                    for station in self.get('airport_map').stations:
                        if station.plane is not None and station.plane.id == plane_jid:
                            # Send query-if to control tower
                            package = Package('takeoff request', station.pos)
                            control_tower = self.get('control_tower')
                            if control_tower:
                                msg = Message(to=control_tower)
                                msg.set_metadata("performative", "query-if")
                                msg.body = jsonpickle.encode(package)

                                await self.send(msg)
                                print('Station manager: takeoff request sent to control tower!')
                                break

            elif performative == 'inform':
                # Inform that airstrip is available
                # Send inform for plane to leave station
                package = jsonpickle.decode(msg.body)
                type = package.message
                if type == 'available airstrip':
                    airstrip_pos, plane_id = package.body

                    # Set station as available
                    for station in self.get('airport_map').stations:
                        if station.plane is not None and station.plane.id == plane_id:
                            station.plane = None
                            station.state = 0
                    
                            # Send inform to plane
                            package = Package('available airstrip', airstrip_pos)
                            
                            msg = Message(to=plane_id)
                            msg.set_metadata("performative", "inform")
                            msg.body = jsonpickle.encode(package)

                            await self.send(msg)
                            print('Station manager: available airstrip sent to plane!')

                            break
