from bitmex.GlobalSettings import GlobalSettings
from bitmex.bitmexDataHandler import bitmexDataHandler
# from bitmex.OMS import bitmexTargetPositionOMS
from event.eventEngine import eventEngine
from event.eventType import *
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
        self.data_handler.register_bar_event('XBTUSD', '15s')

        # # strategy
        # strategy_configs = [
        #     {
        #         'symbol': 'XBTUSD',
        #         'bar_type': '1m',
        #         'params': {'slow': 5, 'fast': 10},
        #     }
        # ]
        # config = strategy_configs[0]
        # self.strategy = MaStrategy(config['symbol'], config['bar_type'], config['params'])
        #
        # self.strategy.add_event_engine(self.event_engine)
        # self.event_engine.register(EVENT_TICK, self.strategy.on_tick)
        # self.event_engine.register(EVENT_BAR_OPEN, self.strategy.on_bar_open)
        # self.event_engine.register(EVENT_BAR_CLOSE, self.strategy.on_bar_close)
        #
        # # portfolio
        # self.portfolio = NaivePortfolio()
        #
        # self.portfolio.add_event_engine(self.event_engine)
        # self.event_engine.register(EVENT_SIGNAL, self.portfolio.on_signal_event)
        #
        # # executor
        # self.oms = bitmexTargetPositionOMS()
        #
        # self.oms.add_event_engine(self.event_engine)
        # self.event_engine.register(EVENT_TARGET_POSITION, self.oms.on_target_position_event)
        # self.event_engine.register(EVENT_ORDERBOOK, self.oms.on_orderbook_event)


    def start(self):
        self.event_engine.start()   # 启动事件引擎
        self.data_handler.run()     # 启动数据引擎

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
