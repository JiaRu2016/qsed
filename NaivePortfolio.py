from .portfolio import Portfolio


class NaivePortfolio(Portfolio):
    """
    NaivePortfolio: simply convert long / short Signal to 1 lot corresponding order
    use limit order, limit price = best bid or ask
    """

    def __init__(self, event_queue, data_handler):
        self.event_queque = event_queue
        self.data_handler = data_handler

    def on_signal_event(self, event):
        pass

    def on_fill_event(self, event):
        pass

    def on_market_event(self, event):
        pass