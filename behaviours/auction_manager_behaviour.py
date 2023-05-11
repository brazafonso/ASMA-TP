from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
from spade.message import Message
from objects.package import Package
from objects.auction import Auction

import jsonpickle

class AuctionManagerCleanerBehaviour(PeriodicBehaviour):

    # TODO: Increase budget of airline per number of stations
    
    async def run(self):
        check_bids = [] # (station.id, airline.jid, bid)
        with self.agent.stations_lock:
            for station, auction in self.agent.stations.values():
                # Check if auction is over
                if auction and auction.is_over():
                    # Check if winner has enough money
                    airline_winner_jid = auction.winning_bid.bidder_jid
                    biggest_bid = auction.winning_bid
                    check_bids.append((station.id, airline_winner_jid, biggest_bid))
        
        update_owners = [] # (station.id, airline.name)

        # Check if the winners have enough money
        with self.agent.airlines_lock:
            for station_id, airline_jid, bid in check_bids:
                if airline_jid in self.agent.airlines:
                    airline = self.agent.airlines[airline_jid]
                    if airline.budget >= bid.value:
                        # Send accept proposal
                        pkg = Package("bid accepted", bid)
                        msg = Message(to=airline_jid)
                        msg.set_metadata("performative", "accept-proposal")
                        msg.body = jsonpickle.encode(pkg)

                        await self.send(msg)

                        # Update station owner
                        # Get airline name
                        airline_name = self.agent.airlines[airline_jid].name
                        update_owners.append((station_id, airline_name))

                        # Update airline budget
                        self.agent.airlines[airline_jid].budget -= bid.value

                    else:
                        # Send reject proposal
                        pkg = Package("bid rejected", bid)
                        msg = Message(to=airline_jid)
                        msg.set_metadata("performative", "reject-proposal")
                        msg.body = jsonpickle.encode(pkg)

                        await self.send(msg)
            
        # Update station owners and remove auctions
        with self.agent.stations_lock:
            for station_id, airline_name in update_owners:
                station = self.agent.stations[station_id][0]
                station.airline_name = airline_name
                self.agent.stations[station_id] = (station, None)
            
            # Update station ownwers in AirportMap object
            stations = []
            for station, auction in self.agent.stations.values():
                stations.append(station.get_copy())

            self.get('airport_map').update_stations(stations)

class AuctionManagerUpdateAirlinesBehaviour(PeriodicBehaviour):
    """Atualização das bids das diferentes airlines pelas stations disponíveis."""

    async def run(self):
        # Copy the airlines list
        airlines = []
        with self.agent.airlines_lock:
            airlines = self.agent.airlines.copy()
        
        for airline in airlines.values():
            airline_id = airline.jid
            airline_type = airline.type
            
            stations_of_type = [] # [(auction_state, station))]
            with self.agent.stations_lock:
                for station, auction in self.agent.stations.items():
                    if station.type == airline_type:
                        auction_state = None
                        if auction and not auction.is_over():
                            auction_state = auction.state
                        stations_of_type.append((auction_state, station))
            
            pkg = Package("available stations", (airline, stations_of_type))
            msg = Message(to=airline_id)
            msg.set_metadata("performative", "inform")
            msg.body = jsonpickle.encode(pkg)

            await self.send(msg)

class AuctionManagerListenerBehaviour(CyclicBehaviour):
    """Gestão das bids das diferentes airlines pelas stations disponíveis."""

    async def run(self):
        self.agent.write_log("Auction Manager Behaviour Running")

        msg = await self.receive(timeout=15)
        # Possible messages:
        # - Request to get available stations
        # - Bids from airlines
        if msg:
            self.agent.write_log("Auction Manager Behaviour: Got message")
            performative = msg.get_metadata('performative')
            pkg = jsonpickle.decode(msg.body)
            if performative == 'subscribe':
                type = pkg.message
                if type == 'subscribe auction':
                    simple_airline = pkg.body
                    with self.agent.airlines_lock:
                        self.agent.airlines[simple_airline.jid] = simple_airline
                    
                    self.agent.write_log("Auction Manager Behaviour: Airline {} subscribed".format(msg.sender))

            elif performative == 'propose':
                type = pkg.message
                if type == 'bids':
                    bids = pkg.body # [(station.id, bid)]
                    with self.agent.stations_lock:
                        for bid_pair in bids:
                            station_id = bid_pair[0]
                            bid = bid_pair[1]
                            if station_id in self.agent.stations:
                                if self.agent.stations[station_id][1]:
                                    if bid.is_buy():
                                        bid_success = self.agent.stations[station_id][1].add_bid(bid)
                                        pkg = Package("bid status", (bid_success, bid))
                                        msg = Message(to=msg.sender)
                                        msg.set_metadata("performative", "inform")
                                        msg.body = jsonpickle.encode(pkg)

                                        await self.send(msg)
                                
                                # Check if bid is to sell and auction is None
                                elif bid.is_sell():
                                    # Check if the airline owns the station
                                    if self.agent.stations[station_id][0].airline_name == bid.station.airline_name:
                                        station = self.agent.stations[station_id][0]
                                        if station.isEqual(bid.station):
                                            # Create auction (end time is in 30 seconds)
                                            self.agent.stations[station_id] = (station, Auction(bid.value, bid.station))


        else:
            self.agent.write_log("Auction Manager Behaviour: No message received")


class AuctionManagerStatusSender(PeriodicBehaviour):
    '''Periodicamente envia o estado das gares para o station manager'''

    async def run(self):
        self.agent.write_log('Auction manager: Sending stations status to station manager.')

        package = Package('station status report', self.get('airport_map').get_stations())
        msg = Message(to=self.get('station_manager'))
        msg.set_metadata("performative", "inform")
        msg.body = jsonpickle.encode(package)

        await self.send(msg)