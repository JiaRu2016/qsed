class Orderbook(object): 
    def __init__(self, symbol=None, bid1=None, bid1vol=None, ask1=None, ask1vol=None, timestamp=None):
        self.symbol = symbol
        self.bid1 = bid1
        self.bid1vol = bid1vol
        self.ask1 = ask1
        self.ask1vol = ask1vol
        self.timestamp = timestamp
        
    def __repr__(self):
        return self.__dict__.__repr__()
        

class Tick(object): 
    def __init__(self, symbol=None, price=None, volume=None, direction=None, timestamp=None):
        self.symbol = symbol
        self.price = price
        self.volume = volume
        self.direction = direction
        self.timestamp = timestamp
        
    def __repr__(self):
        return self.__dict__.__repr__()


class Bar(object):
    pass


class Snapshot(object):
    pass