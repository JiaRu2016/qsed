from abc import ABCMeta, abstractmethod


class Portfolio(object):
    """
    Portfolio

    - portfolio construction
    - order management
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def on_signal_event(self, event):
        raise NotImplementedError('Must implement on_signal_event()')

    @abstractmethod
    def on_fill_event(self, event):
        raise NotImplementedError('Must implement on_fill_event')

