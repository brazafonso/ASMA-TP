from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
from spade.message import Message
from objects.package import Package
from objects.auction import Auction

import jsonpickle

# TODO: Periodic behaviour to update station owners (result of auctions)
#       - here check if the winners have enough money to buy the station
#       - if not, the station is not sold and the next highest bid is chosen
#       - increment budgets over time
#       - send accept/reject proposal to airlines

class AuctionManagerCleanerBehaviour(PeriodicBehaviour):
    
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

class AuctionManagerNotifyAirlines(PeriodicBehaviour):
    async def run(self):
        with self.agent.notify_success_bid_lock:
            for bid_status in self.agent.notify_success_bid:
                # Send message to airlines
                pkg = Package("bid status", (bid_status[1], bid_status[2])) # (success, bid)
                msg = Message(to=bid_status[0])
                msg.set_metadata("performative", "inform")
                msg.body = jsonpickle.encode(pkg)

                await self.send(msg)

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
                                        with self.agent.notify_success_bid_lock:
                                            self.agent.notify_success_bid.append((msg.sender, bid_success, bid))
                                
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
