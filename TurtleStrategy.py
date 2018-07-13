from .strategy import Strategy
from .event import MarketEvent, SignalEvent


class TurtleStrategy(Strategy):
    """
    TurtleStrategy
    """

    def __init__(self, event_queue, data_handler, para):
        self.event_queue = event_queue
        self.data_handler = data_handler
        self.para = para

    def on_market_event(self, event):
        """
        MarketEvent 处理函数

        :param event: MarketEvent
        :return:
        """
        if event.type == 'MARKET':
            print('processing MarketEvent:')
            print(event)

            signal_event = SignalEvent()

            self.event_queue.put(signal_event)
