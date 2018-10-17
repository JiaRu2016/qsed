from ctaObject import CtaStrategy
from qsDataStructure import Tick, Bar
from event.eventEngine import Event
from event.eventType import EVENT_SIGNAL
from ctaObject import CtaStrategyConfig
import time


class EmaContext(object):
    """EMA Strategy Context"""

    def __init__(self):
        self.ema_fast = None
        self.ema_slow = None
        self.target_position = 0


class EmaStrategy(CtaStrategy):
    """EMA Strategy

    ema_fast > ema_slow, LONG
    ema_fast < ema_slow, SHORT
    """

    def __init__(self, config):
        super().__init__(config)
        self.context = EmaContext()

        self.event_engine = None
        self.data_handler = None

    def add_evnet_engine(self, event_engine):
        self.event_engine = event_engine

    def add_data_handler(self, data_handler):
        self.data_handler = data_handler

    def on_init(self):
        print('Calling on_init() ...........')
        self.__waiting_for_first_tick()   # todo. this is temp solution

        tick = self.__get_current_tick()
        assert isinstance(tick, Tick), 'class is %s' % tick.__class__
        self.context.ema_fast = tick.price
        self.context.ema_slow = tick.price
        self.__gen_target_positon()

    def __waiting_for_first_tick(self):
        while self.__get_current_tick() is None:
            time.sleep(0.5)

    def on_bar_close(self, event):
        pass

    def on_bar_open(self, event):
        print('Calling strategy.on_bar_open() .........')
        prev_bar = self.__get_prev_bar()

        if prev_bar is None:
            print('~~~~~~~~ prev_bar is None ~~~~~~~~~')
            self.__gen_target_positon()
            print('~~~~~~~~~ target_positon is %s' % self.context.target_position)
            self.__push_signal_event()
            return

        assert isinstance(prev_bar, Bar), 'class is %s' % prev_bar.__class__
        new_price = prev_bar.close
        alpha_fast = 2 / (self.para['fast'] + 1)
        alpha_slow = 2 / (self.para['slow'] + 1)
        self.context.ema_fast = alpha_fast * new_price + (1 - alpha_fast) * self.context.ema_fast
        self.context.ema_slow = alpha_slow * new_price + (1 - alpha_slow) * self.context.ema_slow

        self.__gen_target_positon()
        self.__push_signal_event()

    def __gen_target_positon(self):
        if self.context.ema_fast > self.context.ema_slow:
            self.context.target_position = 1
        elif self.context.ema_fast < self.context.ema_slow:
            self.context.target_position = -1
        else:
            self.context.target_position = 0

    def on_tick(self, event):
        pass

    def __get_current_bar(self):
        return self.data_handler.get_current_bar(self.symbol, self.bar_type)

    def __get_prev_bar(self):
        return self.data_handler.get_prev_bar(self.symbol, self.bar_type)

    def __get_current_tick(self):
        return self.data_handler.get_current_tick(self.symbol)

    def __push_signal_event(self):
        e = Event(type_=EVENT_SIGNAL)
        e.dict_ = {'identifier': self.identifier, 'symbol': self.symbol, 'target_position': self.context.target_position}
        self.event_engine.put(e)
        print('🎲 🎲 🎲 🎲  pushing signal event 🎲 🎲 🎲 🎲  strategy target_position is %s' % self.context.target_position)