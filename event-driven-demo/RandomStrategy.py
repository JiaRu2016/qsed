from qsObject import Strategy
from qsEvent import MarketEvent, SignalEvent
import time
import random


class RandomStrategy(Strategy):
    """
    TurtleStrategy
    """

    def __init__(self, event_queue, data_handler):
        self.event_queue = event_queue
        self.data_handler = data_handler

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

            # 构造SignalEvent
            symbol = 'IF'
            rand_signal = random.sample([1, 0, 1], k=1)[0]
            now = time.time()
            signal_event = SignalEvent(symbol=symbol, timestamp=now, signal_direction=rand_signal)

            # 放入事件队列
            self.event_queue.put(signal_event)
