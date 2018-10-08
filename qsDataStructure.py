import copy


class MarketData(object):
    """行情数据类"""

    def __repr__(self):
        return self.__dict__.__repr__()

    def copy(self):
        return copy.deepcopy(self)


class Orderbook(MarketData):
    def __init__(self, symbol=None, bid1=None, bid1vol=None, ask1=None, ask1vol=None, timestamp=None, receive_time=None):
        self.symbol = symbol
        self.bid1 = bid1
        self.bid1vol = bid1vol
        self.ask1 = ask1
        self.ask1vol = ask1vol
        self.timestamp = timestamp
        self.receive_time = receive_time


class Tick(MarketData):
    def __init__(self, symbol=None, price=None, volume=None, direction=None, timestamp=None, receive_time=None):
        self.symbol = symbol
        self.price = price
        self.volume = volume
        self.direction = direction
        self.timestamp = timestamp
        self.receive_time = receive_time


class Bar(MarketData):
    def __init__(self, symbol=None, bar_type=None, td=None, ts=None, open=None, high=None, low=None, close=None, timestamp=None, receive_time=None):
        self.symbol = symbol
        self.bar_type = bar_type
        self.td = td
        self.ts = ts
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = None   # TODO: vol, amt, vwap, ticks
        self.amount = None
        self.vwap = None
        self.ticks = None
        self.timestamp = timestamp         # timestamp of last_price which close the bar, ie. new bar's open tick
        self.receive_time = receive_time   # receive_time of last_price which close the bar, ie. new bar's open tick


class Snapshot(MarketData):
    pass

