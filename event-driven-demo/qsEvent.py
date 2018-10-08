# event.py


"""
Events

- MarketEvent, consumed by StrategyObject, and generate
- SignalEvent, consumed by PortfolioObject, and generate
- OrderEvent, handled by ExecutionHandler, generating
- FillEvent, consumed by PortfolioObject, may then produce OrderEvent
"""


class Event(object):
    """
    Event is base class providing an interface for all events, which will trigger further events.
    """
    pass


class MarketEvent(Event):
    """
    MarketEvent
    """

    def __init__(self):
        self.type = 'MARKET'


class SignalEvent(Event):
    """
    SignalEvent
    """

    def __init__(self, symbol, timestamp, signal_direction):
        self.type = 'SIGNAL'
        self.symbol = symbol
        self.timestamp = timestamp
        self.signal_direction = signal_direction   # LONG or SHORT

    def __repr__(self):
        return "<SignalEvent> [%s] %s %s" % (self.timestamp, self.symbol, self.signal_direction)


class OrderEvent(Event):
    """
    OrderEvent
    """

    def __init__(self, timestamp, symbol, order_type, direction, quantity, price=0.0):
        self.type = 'ORDER'
        self.timestamp = timestamp
        self.symbol = symbol
        self.order_type = order_type   # 'MKT', 'LMT' OR 'CANCEL_ORDER_REQ'
        self.direction = direction     # 'BUY' or 'SELL'
        self.quantity = quantity       # non-negative integer
        self.price = price             # limit order price. If market order, this field is ignored

    def __repr__(self):
        return "<OrderEvent> [%s] %s %s %s %d @ %.2f" % (self.timestamp, self.symbol, self.order_type, self.direction, self.quantity, self.price)


class FillEvent(Event):
    """
    FillEvent
    """

    def __init__(self, timestamp, symbol, direction, quantity, price, commission, fill_flag):
        self.type = 'FILL'
        self.timestamp = timestamp     # timestamp of Fill
        self.symbol = symbol
        self.direction = direction     # 'BUY' or 'SELL'
        self.quantity = quantity       # filled quantity
        self.price = price             # average price of filled orders
        self.commission = commission   # commission increment
        self.fill_flag = fill_flag     # 'PARTIAL', 'ALL', 'CANCELED'

    def __repr__(self):
        return "<FillEvent> [%s] %s %s %d@%.2f" % (self.timestamp, self.symbol, self.direction, self.quantity, self.price)

