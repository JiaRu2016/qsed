from abc import ABCMeta, abstractmethod


class QsObject(object):
    """qs object

    basic: DataHandler, Strategy, Profolio, Executor
    advanced: RiskManager etc.
    """
    def add_event_engine(self, event_engine):
        self.event_engine = event_engine

    def add_data_handler(self, data_handler):
        self.data_handler = data_handler


class DataHandler(QsObject):
    """
    TODO: split bimtexDataHandler
    """

    __metaclass__ = ABCMeta

    def add_data_handler(self, data_handler):
        """intended to override it"""
        pass


class Strategy(QsObject):
    """
    Strategy
    """

    __metaclass__ = ABCMeta


    @abstractmethod
    def on_init(self):
        raise NotImplementedError

    @abstractmethod
    def on_bar_close(self):
        raise NotImplementedError

    @abstractmethod
    def on_bar_open(self):
        raise NotImplementedError

    @abstractmethod
    def on_tick(self):
        raise NotImplementedError


class Portfolio(QsObject):
    """
    Portfolio
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def on_signal_event(self, event):
        raise NotImplementedError


class ExecutionHandler(QsObject):
    """
    TODO: encapsulate bitmex.OMS
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def on_target_position_event(self):
        raise NotImplementedError
