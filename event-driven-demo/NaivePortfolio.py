from qsObject import Portfolio
from qsEvent import OrderEvent, SignalEvent
import datetime


class NaivePortfolio(Portfolio):
    """
    NaivePortfolio: simply convert long / short Signal to 1 lot corresponding order
    use limit order, limit price = signal_price + slippage   # TODO
    """

    def __init__(self, event_queue, data_handler):
        self.event_queue = event_queue
        self.data_handler = data_handler
        self.slippage = 1

    def on_signal_event(self, event):
        print('### portfolio ### processing signal event:')
        print(event)

        assert isinstance(event, SignalEvent)

        if event.type == 'SIGNAL':
            # 构造OrderEvent
            order = OrderEvent(
                timestamp=datetime.datetime.now(),
                symbol=event.symbol,
                order_type='MKT',
                direction=event.signal_direction,
                quantity=1,
                price=0.0,
            )
            # 放入事件队列
            self.event_queue.put(order)

    def on_fill_event(self, event):
        if event.type == 'FILL':
            print('### portfolio ### got FILL_EVENT', event)

    def on_market_event(self, event):
        if event.type == 'MARKET':
            print('### portfolio ### got MARKET_EVENT: ', event)
