from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
from spade.message import Message
from objects.package import Package

import jsonpickle
import time

class StationManagerListener(CyclicBehaviour):
    '''Listener principal do station manager'''

    async def choose_airstrip(self, available_airstrips, plane, retries=1):
        if retries == 0:
            return None, None
        closest_airstrip = None
        closest_station = None
        min_distance = None
        for airstrip in available_airstrips:
            # Check if this airstrip is in the pending arrivals
            airstrip_available = True
            for pending_airstrip_id, _ in self.agent.pending_arrivals.values():
                if pending_airstrip_id == airstrip.id:
                    airstrip_available = False
                    break
            
            if airstrip_available:
                for station in self.get('airport_map').stations:
                    if station.id not in self.agent.pending_arrivals and station.state == 0 and station.type == plane.type:
                        if closest_station is None:
                            closest_airstrip = airstrip
                            closest_station = station
                            min_distance = airstrip.pos.distance(station.pos)
                        else:
                            distance = airstrip.pos.distance(station.pos)
                            if distance < min_distance:
                                closest_airstrip = airstrip
                                closest_station = station
                                min_distance = distance
        
        # If the values are still None, retry
        if closest_airstrip is None or closest_station is None:
            return await self.choose_airstrip(available_airstrips, plane, retries-1)

        # Make the reservation
        key = closest_station.id
        val = (closest_airstrip.id, time.time(),plane)

        def_val = self.agent.pending_arrivals.setdefault(key, val)

        # If the key already existed, the value is an old reservation, so we try again
        if val[0] != def_val[0] or val[1] != def_val[1]:
            return await self.choose_airstrip(available_airstrips, plane, retries-1)
        
        # If the key didn't exist, we have a new reservation
        # We still need to check if the airstrip is still available
        # This is used to keep the pending arrivals consistent
        else:
            airstrip_available = True
            for pending_station in self.agent.pending_arrivals:
                if pending_station != closest_station.id:
                    if self.agent.pending_arrivals[pending_station][0] == closest_airstrip.id:
                        airstrip_available = False
                        break
            
            if not airstrip_available:
                del self.agent.pending_arrivals[key]
                return await self.choose_airstrip(available_airstrips, plane, retries-1)
            else:
                return closest_airstrip, closest_station

    async def run(self):
        # Get message
        msg = await self.receive(timeout=10)
        
        # Possible messages:
        # - Query-if to check if station is available
        # - Request to leave station
        # - Inform to inform that airstrip is available (allow request to leave station)
        if msg:
            print('Station Manager: ','Got message')
            performative = msg.get_metadata('performative')
            if performative == 'query-if':
                # Check if station is available
                # If available, send inform
                # Update station state
                package = jsonpickle.decode(msg.body)
                type = package.message
                if type == 'landing request':
                    available_airstrips, plane = package.body

                    closest_airstrip, closest_station = await self.choose_airstrip(available_airstrips, plane, retries=10)

                    if closest_station is not None and closest_airstrip is not None:
                        package = Package('available station',(closest_airstrip, closest_station,plane))
                        control_tower = self.get('control_tower')
                        if control_tower:
                            msg = Message(to=control_tower)
                            msg.set_metadata("performative", "inform")
                            msg.body = jsonpickle.encode(package)

                            await self.send(msg)
                            print('Station manager: available station sent!')
                    else:
                        print('Station manager: no available station.')
                        # TODO: Handle falta de gares

            elif performative == 'request':
                # Request to leave station
                # If everything OK, send query-if to control tower
                package = jsonpickle.decode(msg.body)
                type = package.message
                if type == 'takeoff request':
                    print('Station manager: Take off request received.')
                    plane_jid = package.body
                    # Check if plane is in station
                    for station in self.get('airport_map').stations:
                        print('Station manager: Checking if plane is in station')
                        if station.state == 1 and station.plane is not None and station.plane.id == plane_jid:
                            # Send query-if to control tower
                            package = Package('takeoff request', (station.pos,station.plane))
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

                if type == 'confirm pending arrival':
                    print('Station manager: confirmation of pending arrival.')
                    station_id = package.body
                    if station_id in self.agent.pending_arrivals:
                        print('Station manager: reserving station')
                        _,_,plane = self.agent.pending_arrivals[station_id]
                        result = self.get('airport_map').reserve_station(station_id,plane)
                        if result :
                            del self.agent.pending_arrivals[station_id]


                elif type == 'available airstrip':
                    airstrip_pos, plane_id = package.body
                    print('Station manager: available airstrip.')
                    # Set station as available
                    for station in self.get('airport_map').stations:
                        if station.plane is not None and station.plane.id == plane_id:
                            station.plane = None
                            station.state = 0
                    
                            # Send inform to plane
                            package = Package('available airstrip', airstrip_pos)
                            
                            msg = Message(to=str(plane_id))
                            msg.set_metadata("performative", "inform")
                            msg.body = jsonpickle.encode(package)

                            await self.send(msg)
                            print('Station manager: available airstrip sent to plane!')

                            break


class StationManagerClearOldReservationsBehaviour(PeriodicBehaviour):
    async def run(self):
        # Clear old reservations
        current_time = time.time()
        for station_id in self.agent.pending_arrivals:
            _, timestamp,_ = self.agent.pending_arrivals[station_id]
            if current_time - timestamp > 15: # TODO: Definir...
                del self.agent.pending_arrivals[station_id]
                print('Station manager: cleared old reservation, station id: ' + str(station_id))
