from spade.behaviour import PeriodicBehaviour, CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from objects.package import Package
from objects.bid import Bid
from objects.auction import Auction

import jsonpickle
import random


class AirlineSubscribeToAuctionManager(OneShotBehaviour):
    '''Subscribe auction notifications from the auction manager'''
    async def run(self):
        # Request the list of available stations
        pkg = Package("subscribe auction", self.agent.airline.get_simple_object())
        msg = Message(to=self.get('auction_manager'))
        msg.set_metadata("performative", "subscribe")
        msg.body = jsonpickle.encode(pkg)

        await self.send(msg)

class AirlineListenerBehaviour(CyclicBehaviour):
    async def run(self):

        # Check if subscribed to the auction manager
        if not self.agent.subscribed:
            self.agent.add_behaviour(AirlineSubscribeToAuctionManager())
        
        msg = await self.receive(timeout=15)
        # Possible messages:
        # - Inform of the available stations
        # - Accept/Reject of the bids
        if msg:
            self.agent.write_log("Airline Listener Behaviour ({}): Got message".format(self.agent.jid))
            performative = msg.get_metadata('performative')
            pkg = jsonpickle.decode(msg.body)
            type = pkg.message
            if performative == 'inform':
                if type == 'available stations':
                    updated_airline = pkg.body[0]
                    self.agent.airline.update(updated_airline)
        
                    updated_stations = pkg.body[1]
                    with self.agent.available_stations_lock:
                        self.agent.available_stations = (False, updated_stations)
                elif type == 'bid status':
                    success, bid = pkg.body
                    if not success:
                        # Remove bid from my_bids
                        with self.agent.my_bids_lock:
                            if bid.station.id in self.agent.my_bids:
                                self.agent.my_bids.remove(bid.station.id)
                elif type == 'confirm subscription':
                    self.agent.subscribed = True
                    self.agent.write_log("Airline Listener Behaviour({}): Subscribed to Auction Manager".format(self.agent.jid))

            elif performative == 'accept-proposal':
                if type == 'bid accepted':
                    self.agent.write_log("Airline Listener Behaviour ({}): Bid accepted".format(self.agent.jid))
                    accepted_bid = pkg.body
                    with self.agent.my_bids_lock:
                        if accepted_bid.station.id in self.agent.my_bids:
                            self.agent.my_bids.remove(accepted_bid.station.id)

            elif performative == 'reject-proposal':
                if type == 'bid rejected':
                    self.agent.write_log("Airline Listener Behaviour ({}): Bid rejected".format(self.agent.jid))
                    rejected_bid = pkg.body
                    with self.agent.my_bids_lock:
                        if rejected_bid.station.id in self.agent.my_bids:
                            self.agent.my_bids.remove(rejected_bid.station.id)

class AirlineBiddingBehaviour(PeriodicBehaviour):
    '''Comportamento de bidding da companhia aerea'''

    def get_bid(self, auction_state, station):
        
        balance_after_bids = self.agent.airline.budget
        with self.agent.my_bids_lock:
            for bid in self.agent.my_bids.values():
                balance_after_bids -= bid[1].value
        
        # There is an auction for this station
        if auction_state:
            # Auction is open
            if auction_state == Auction.OPEN:
                # If we are not owner, we might bid
                if station.airline_name != self.agent.airline.name:

                    with self.agent.my_bids_lock:

                        # Check current bids size
                        if len(self.agent.my_bids) >= self.agent.airline.max_bids:
                            self.agent.write_log("Airline Bidding Behaviour ({}): Max bids reached".format(self.agent.jid))
                            return None

                        # Check if already bid for this station
                        elif any(bid.station.id == station.id for bid in self.agent.my_bids.values()):
                            self.agent.write_log("Airline Bidding Behaviour ({}): Already bid for this station".format(self.agent.jid))
                            return None
                        
                    # Check if we have enough money
                    if balance_after_bids * self.agent.airline.relative_max_bid < station.base_value:
                        self.agent.write_log("Airline Bidding Behaviour ({}): Not enough money".format(self.agent.jid))
                        return None
                    
                    # Generate random increment to base value
                    increment = station.base_value * random.uniform(0, self.agent.airline.relative_max_increment)
                    
                    bid_value = min(station.base_value + increment, balance_after_bids * self.agent.airline.relative_max_bid)
                    return Bid(self.airline.jid, Bid.BUY, bid_value, station)
                        

            elif auction_state == Auction.CLOSED:
                # Do nothing
                return None
            else:
                self.agent.write_log("Airline Bidding Behaviour ({}): Invalid auction state {} for station {}".format(self.agent.jid, auction_state, station.id))
                return None
        
        # No auction for this station
        else:
            # Check if we are owner, if so, we can sell
            if station.airline_name == self.agent.airline.name:
                
                # Check if costs are bigger than budget, if so, sell...
                if self.agent.airline.costs > balance_after_bids:
                    return Bid(self.airline.jid, Bid.SELL, station.base_value, station)

        return None

    async def run(self):

        # Check if available_stations were seen
        with self.agent.available_stations_lock:
            seen = self.agent.available_stations[0]
            stations = self.agent.available_stations[1]
            self.agent.available_stations = (True, []) # Mark as seen


        if seen:
            self.agent.write_log("Airline Bidding Behaviour ({}): Already seen available stations".format(self.agent.jid))
        else:
            self.agent.write_log("Airline Bidding Behaviour ({}): New available stations".format(self.agent.jid))

            bids = []
            for auction_state, station in stations:
                bid = self.get_bid(auction_state, station)
                if bid:
                    bids.append((station.id, bid))
            
            # Send bids to auction manager
            if bids:
                pkg = Package("bids", bids)
                msg = Message(to=self.get('auction_manager'))
                msg.set_metadata("performative", "propose")
                msg.body = jsonpickle.encode(pkg)

                await self.send(msg)

                with self.agent.my_bids_lock:
                    for bid in bids:
                        self.agent.my_bids[bid[0]] = bid[1]

                self.agent.write_log("Airline Bidding Behaviour ({}): Sent bids".format(self.agent.jid))
