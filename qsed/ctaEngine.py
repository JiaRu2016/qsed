from bitmex.bitmexAccountSettings import bitmexAccountSettings
from bitmexDataHandler import bitmexDataHandler
from bitmexTargetPositionExecutor import bitmexTargetPositionExecutor

from event.eventEngine import eventEngine
from event.eventType import EVENT_ORDERBOOK, EVENT_TICK, EVENT_BAR_OPEN, EVENT_BAR_CLOSE, EVENT_SIGNAL, EVENT_TARGET_POSITION
from strategy import STRATEGY_CLASS
from CtaNaivePortfolio import CtaNaivePortfolio
from ctaObject import CtaPortfolioSettings, CtaStrategyConfig

import json


class CtaEngine(object):
    """主引擎"""

    def __init__(self, g, bitmex_account_settings, cta_settings):

        # 全局设置
        self.g = g

        # bitmex账户设置
        self.bitmex_account_settings = bitmex_account_settings

        # 事件引擎
        self.event_engine = eventEngine()

        # 数据引擎 DataHandler
        self.data_handler = bitmexDataHandler(self.g, self.bitmex_account_settings)
        self.data_handler.add_event_engine(self.event_engine)

        assert isinstance(cta_settings, CtaPortfolioSettings)

        self.data_handler.set_symbols(cta_settings.symbols)

        for sym in cta_settings.symbols:
            self.data_handler.register_tick_event(sym)
            self.data_handler.register_orderbook_event(sym)

        for d in cta_settings.bar_types:
            assert isinstance(d, dict) and d.__len__() == 1
            self.data_handler.register_bar_event(list(d.keys())[0], list(d.values())[0])

        # strategy
        self.strategy_pool = []

        for config in cta_settings.strategy_configs:
            strategy = self.__construct_strategy_instance(config)
            strategy.add_data_handler(self.data_handler)
            strategy.add_event_engine(self.event_engine)
            self.strategy_pool.append(strategy)

        for strategy in self.strategy_pool:
            config = strategy.config
            self.event_engine.register(EVENT_TICK, strategy.on_tick)
            self.event_engine.register(EVENT_BAR_OPEN % (config.symbol, config.bar_type), strategy.on_bar_open)
            self.event_engine.register(EVENT_BAR_CLOSE % (config.symbol, config.bar_type), strategy.on_bar_close)

        # portfolio  TODO: multiple portfolios
        self.portfolio = CtaNaivePortfolio()
        self.portfolio.add_event_engine(self.event_engine)
        self.portfolio.config(identifier_multiplier=cta_settings.portfolio, symbol_multiplier=cta_settings.symbol_multiplier)
        self.event_engine.register(EVENT_SIGNAL, self.portfolio.on_signal_event)

        # executor
        self.executor = bitmexTargetPositionExecutor(self.g, self.bitmex_account_settings, cta_settings.symbols)
        self.executor.add_event_engine(self.event_engine)
        self.executor.add_data_handler(self.data_handler)

        self.event_engine.register(EVENT_TARGET_POSITION, self.executor.on_target_position_event)
        self.event_engine.register(EVENT_TICK, self.executor.on_tick_event)
        self.event_engine.register(EVENT_ORDERBOOK, self.executor.on_orderbook_event)

    def __construct_strategy_instance(self, config):
        assert isinstance(config, CtaStrategyConfig)
        if config.strategy_name in STRATEGY_CLASS:
            kls = STRATEGY_CLASS[config.strategy_name]
            return kls(config)
        else:
            print('Can not find strategy class: %s' % config.strategy_name)

    def start(self):
        self.event_engine.start()          # 启动事件引擎
        self.data_handler.start()          # 启动数据引擎
        self.data_handler.get_init_data()  # 获取历史回看数据 TODO  正常是先要实时数据，根据第一个tick时间戳再获取历史数据
        for strategy in self.strategy_pool:
            strategy.on_init()             # 策略初始化  todo fix bug: on_init called before first Tick

    def stop(self):
        self.data_handler.stop()
        self.event_engine.stop()


    def monitor_event_engine(self):
        """监控主进程事件"""
        pass


class GlobalSettings(object):
    """
    全局设置

    - 日志级别
    - 日志文件
    - etc...
    """

    def __init__(self):
        self.loglevel = None
        self.logfile = None

    def from_config_file(self, file):
        with open(file) as f:
            st = json.load(f)
        self.loglevel = st['log']['loglevel']
        self.logfile = st['log']['logfile']



if __name__ == '__main__':

    import time

    g = GlobalSettings()
    g.from_config_file('./global_settings.json')

    bitmex_account_settings = bitmexAccountSettings()
    bitmex_account_settings.from_config_file('bitmex/BITMEX_connect.json', which="account_real_trading")

    cta_settings = CtaPortfolioSettings()
    cta_settings.from_config_file()
    cta_settings.check()

    me = CtaEngine(g, bitmex_account_settings, cta_settings)
    me.start()
    time.sleep(120)
    me.stop()
