from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
from spade.message import Message
from objects.package import Package

import jsonpickle
import time


class StationManagerListener(CyclicBehaviour):
    '''Listener principal do station manager'''

    async def choose_airstrip(self, stations, available_airstrips, plane, retries=1):
        if retries == 0:
            return None, None
        
        closest_airstrip = None
        closest_station = None
        min_distance = None
        async with self.agent.pending_arrivals_lock:
            for airstrip in available_airstrips.values():
                # Check if this airstrip is in the pending arrivals
                airstrip_available = True
                for station_id in self.agent.pending_arrivals:
                    pending_airstrip_id, _,_ = self.agent.pending_arrivals[station_id]
                    if pending_airstrip_id == airstrip.id:
                        airstrip_available = False
                        break
                    
                # Check closest station to this airstrip
                if airstrip_available:
                    for station in stations.values():
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
            return await self.choose_airstrip(stations, available_airstrips, plane, retries-1)

        # Make the reservation
        key = closest_station.id
        val = (closest_airstrip.id, time.time(), plane)

        async with self.agent.pending_arrivals_lock:
            def_val = self.agent.pending_arrivals.setdefault(key, val)
        # If the key already existed, the value is an old reservation, so we try again
        if val[0] != def_val[0] or val[1] != def_val[1]:
            return await self.choose_airstrip(stations, available_airstrips, plane, retries-1)
        
        # If the key didn't exist, we have a new reservation
        # We still need to check if the airstrip is still available
        # This is used to keep the pending arrivals consistent
        else:
            airstrip_available = True
            async with self.agent.pending_arrivals_lock:
                for pending_station in self.agent.pending_arrivals:
                    if pending_station != closest_station.id:
                        if self.agent.pending_arrivals[pending_station][0] == closest_airstrip.id:
                            airstrip_available = False
                            break
                if not airstrip_available:
                    del self.agent.pending_arrivals[key]
                    return await self.choose_airstrip(stations, available_airstrips, plane, retries-1)
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
            self.agent.write_log('Station Manager: Got message')
            performative = msg.get_metadata('performative')
            if performative == 'query-if':
                # Check if station is available
                # If available, send inform
                # Update station state
                package = jsonpickle.decode(msg.body)
                type = package.message
                if type == 'landing request':
                    available_airstrips, plane = package.body

                    stations = self.get('airport_map').get_stations()
                    closest_airstrip, closest_station = await self.choose_airstrip(stations, available_airstrips, plane, retries=10)

                    if closest_station is not None and closest_airstrip is not None:
                        package = Package('available station',(closest_airstrip, closest_station,plane))
                        control_tower = self.get('control_tower')
                        if control_tower:
                            msg = Message(to=control_tower)
                            msg.set_metadata("performative", "inform")
                            msg.body = jsonpickle.encode(package)

                            await self.send(msg)
                            self.agent.write_log('Station manager: Available station sent!')
                    else:
                        self.agent.write_log('Station manager: No available station.')

            elif performative == 'request':
                # Request to leave station
                # If everything OK, send query-if to control tower
                package = jsonpickle.decode(msg.body)
                type = package.message
                if type == 'takeoff request':
                    self.agent.write_log('Station manager: Take off request received.')
                    plane_jid = package.body
                    station = self.get('airport_map').isPlaneInStation(plane_jid)
                    # Check if plane is in station, if yes, send query-if to control tower
                    if station:
                        # Send query-if to control tower
                        package = Package('takeoff request', (station.pos,station.plane))
                        control_tower = self.get('control_tower')
                        if control_tower:
                            msg = Message(to=control_tower)
                            msg.set_metadata("performative", "query-if")
                            msg.body = jsonpickle.encode(package)

                            await self.send(msg)
                            self.agent.write_log('Station manager: Takeoff request sent to control tower!')

            elif performative == 'inform':
                # Inform that airstrip is available
                # Send inform for plane to leave station
                package = jsonpickle.decode(msg.body)
                type = package.message

                if type == 'confirm pending arrival':
                    self.agent.write_log('Station manager: Confirmation of pending arrival.')
                    station_id = package.body
                    async with self.agent.pending_arrivals_lock:
                        if station_id in self.agent.pending_arrivals:
                            self.agent.write_log('Station manager: Reserving station')
                            _,_,plane = self.agent.pending_arrivals[station_id]
                            result =  self.get('airport_map').reserve_station(station_id,plane)
                            if result :
                                del self.agent.pending_arrivals[station_id]


                elif type == 'available airstrip':
                    airstrip, plane_id = package.body
                    self.agent.write_log('Station manager: Available airstrip.')

                    # Set station as available, return the new station
                    station =  self.get('airport_map').free_station(plane_id=plane_id)

                    # Send inform to plane
                    package = Package('available airstrip', (airstrip,station))
                    
                    msg = Message(to=str(plane_id))
                    msg.set_metadata("performative", "inform")
                    msg.body = jsonpickle.encode(package)
                    
                    await self.send(msg)
                    self.agent.write_log('Station manager: Available airstrip sent to plane!')

                elif type == 'cancel arrival':
                    plane = package.body
                    self.agent.write_log('Station manager: Plane not arriving.')
                    await self.delete_arrival(plane)
                
                elif type == 'station status report':
                    stations = package.body
                    self.agent.write_log('Station manager: Updating stations status.')
                    self.get('airport_map').update_stations(stations)


    async def delete_arrival(self,plane):
        keys_to_delete = []
        async with self.agent.pending_arrivals_lock:
            for station_id in self.agent.pending_arrivals:
                _, _,p = self.agent.pending_arrivals[station_id]
                if plane.id == p.id:
                    keys_to_delete.append(station_id)
        
            for key in keys_to_delete:
                del self.agent.pending_arrivals[key]
        
class StationManagerClearOldReservationsBehaviour(PeriodicBehaviour):
    async def run(self):
        # Clear old reservations
        current_time = time.time()
        async with self.agent.pending_arrivals_lock:
            keys_to_delete = []
            for station_id in self.agent.pending_arrivals:
                _, timestamp,_ = self.agent.pending_arrivals[station_id]
                if current_time - timestamp > 15:
                    keys_to_delete.append(station_id)
                    
            for station_id in keys_to_delete:
                if station_id in self.agent.pending_arrivals:
                    del self.agent.pending_arrivals[station_id]
                    self.agent.write_log('Station manager: Cleared old reservation, station id: ' + str(station_id))


class StationManagerStatusSender(PeriodicBehaviour):
    '''Periodicamente envia o estado das gares para a torre de controlo'''

    async def run(self):
        self.agent.write_log('Station manager: Sending stations status.')

        package = Package('station status report', self.get('airport_map').get_stations())
        msg = Message(to=self.get('control_tower'))
        msg.set_metadata("performative", "inform")
        msg.body = jsonpickle.encode(package)

        await self.send(msg)
