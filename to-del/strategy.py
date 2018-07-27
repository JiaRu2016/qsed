from abc import ABCMeta, abstractmethod


class Strategy(object):
    """
    Strategy
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def on_market_event(self, event):
        raise NotImplementedError('Must implement on_market_event')
