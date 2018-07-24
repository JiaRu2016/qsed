from strategy import Strategy
from event import MarketEvent, SignalEvent
from data_handler import DataHandler


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
            print('=== strategy === processing MarketEvent:', event)

            current_bar = self.data_handler.get_current_bar()
            print('=== strategy === current_bar: ', dict(current_bar))

            # TODO on_bar, on_tick etc.
            signal_event = SignalEvent(symbol='IF', timestamp=-99, signal_direction=1)

            self.event_queue.put(signal_event)
