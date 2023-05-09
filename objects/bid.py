
class Bid:
    """Represents a bid on an item."""

    BUY = 'buy'
    SELL = 'sell'

    def __init__(self, bidder_jid, type, value, station):
        self.bidder_jid = bidder_jid
        self.type = type # 'buy' or 'sell'
        self.value = value
        self.station = station
    
    def is_buy(self):
        return self.type == Bid.BUY
    
    def is_sell(self):
        return self.type == Bid.SELL
