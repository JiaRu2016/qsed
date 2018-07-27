from abc import ABCMeta, abstractmethod


class DataHandler(object):
    """
    DataHandler is abc proving an interface for all inherited data handlers, both live and historic
    The goal of a (derived) DataHandler object is to
        - interface to get history bars/ticks
        - "drip feed" updated bars
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_prev_bars(self, n=1, columns=None):
        raise NotImplementedError('Must implement get_latest_bars()')

    @abstractmethod
    def get_current_bar(self, columns=None):
        raise NotImplementedError('Must implement get_latest_bars()')

    @abstractmethod
    def update(self):
        raise NotImplementedError('Must implement update_bars()')
