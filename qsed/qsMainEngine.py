from bitmex.GlobalSettings import GlobalSettings
from bitmex.bitmexDataHandler import bitmexDataHandler
# from bitmex.OMS import bitmexTargetPositionOMS
from event.eventEngine import eventEngine
from event.eventType import EVENT_ORDERBOOK, EVENT_TICK, EVENT_BAR_OPEN, EVENT_BAR_CLOSE, EVENT_SIGNAL, EVENT_TARGET_POSITION
from EmaStrategy import EmaStrategy
from CtaNaivePortfolio import CtaNaivePortfolio
from bitmexTargetPositionExecutor import bitmexTargetPositionExecutor
import queue
import time


class MainEngine(object):
    """主引擎"""

    def __init__(self, g):

        # 全局设置 (bitmex)   # todo: GlobalSetting切分开来，分成通用的(log)和bitmex的
        self.g = g

        # 事件引擎
        self.event_engine = eventEngine()

        # 数据引擎 DataHandler
        self.data_handler = bitmexDataHandler(self.g)  # todo
        self.data_handler.add_event_engine(self.event_engine)
        self.data_handler.register_tick_event('XBTUSD')    # TODO
        self.data_handler.register_bar_event('XBTUSD', '15s')

        strategy_configs = [
            {
                'identifier': 'EmaStrategy_XBTUSD_15s_9999',
                'symbol': 'XBTUSD',
                'bar_type': '15s',
                'para': {'slow': 5, 'fast': 10},
            },
            {
                'identifier': 'EmaStrategy_XBTUSD_15s_8888',
                'symbol': 'XBTUSD',
                'bar_type': '15s',
                'para': {'slow': 15, 'fast': 30},
            }
        ]
        self.strategy_pool = []

        for config in strategy_configs:
            strategy = EmaStrategy(config)
            strategy.add_data_handler(self.data_handler)
            strategy.add_event_engine(self.event_engine)
            self.strategy_pool.append(strategy)

        for strategy in self.strategy_pool:
            self.event_engine.register(EVENT_TICK, strategy.on_tick)
            self.event_engine.register(EVENT_BAR_OPEN, strategy.on_bar_open)
            self.event_engine.register(EVENT_BAR_CLOSE, strategy.on_bar_close)


        # portfolio  TODO: multiple portfolios
        self.portfolio = CtaNaivePortfolio()
        self.portfolio.add_event_engine(self.event_engine)
        identifier_multiplier = {
            'EmaStrategy_XBTUSD_15s_8888': 18,
            'EmaStrategy_XBTUSD_15s_9999': 36
        }
        symbol_multiplier = {
            'XBTUSD': 1
        }
        self.portfolio.config(identifier_multiplier=identifier_multiplier, symbol_multiplier=symbol_multiplier)
        self.event_engine.register(EVENT_SIGNAL, self.portfolio.on_signal_event)

        # executor
        self.executor = bitmexTargetPositionExecutor(self.g)
        self.executor.add_event_engine(self.event_engine)
        self.executor.add_data_handler(self.data_handler)

        self.event_engine.register(EVENT_TARGET_POSITION, self.executor.on_target_position_event)
        self.event_engine.register(EVENT_TICK, self.executor.on_tick_event)
        self.event_engine.register(EVENT_ORDERBOOK, self.executor.on_orderbook_event)

    def start(self):
        self.event_engine.start()          # 启动事件引擎
        self.data_handler.start()          # 启动数据引擎
        self.data_handler.get_init_data()  # 获取历史回看数据 TODO  正常是先要实时数据，根据第一个tcik时间戳再获取历史数据
        for strategy in self.strategy_pool:
            strategy.on_init()             # 策略初始化  todo fix bug: on_init called before first Tick

    def stop(self):
        self.data_handler.stop()
        self.event_engine.stop()


    def monitor_event_engine(self):
        """监控主进程事件"""
        pass


if __name__ == '__main__':

    import time

    g = GlobalSettings()
    g.from_config_file('bitmex/global_settings.json')

    me = MainEngine(g)
    me.start()
    time.sleep(120)
    me.stop()
