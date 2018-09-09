from TickBacktestExecutionHandler import TickBacktestExecutionHandler
import queue
import time
import datetime


class CtaEngine(object):
    """
    CTA策略引擎（回测）
    """

    def __init__(self, config_file_dir, backtest_mode='bar',
                 backtest_from=20180101, backtest_to=datetime.datetime.now(), start=-5):
        """Constructor"""

        self.backtest_mode = backtest_mode  # bar or tick
        self.backtest_from = backtest_from
        self.backtest_to = backtest_to
        self.start = start

        self.__queue = queue.Queue()  # 事件队列

        self.data_handler = self.createDataHandler()              # 创建DataHandler
        self.strategy_instances = self.createStrategyInstances()  # 创建（多）策略实例
        self.portfolio = self.createPortfolio()                   # 创建portfolio  TODO:多个产品
        self.execution_handler = self.createExecutionHandler()    # 创建ExecutionHandler

    def createDataHandler(self):
        pass

    def createStrategyInstances(self):
        pass

    def createPortfolio(self):
        pass

    def createExecutionHandler(self):
        pass


    def run(self):
        """
        """

        while True:

            time.sleep(1)
            print('=' * 100)

            if self.data_handler.continue_backtest:
                self.data_handler.update()  # 生成 MarketEvent
            else:
                break

            while True:
                try:
                    event = self.__queue.get(block=False)
                except queue.Empty:
                    break
                else:
                    # 根据事件的不同类型，调用各自的 handlers 处理事件
                    if event.type == 'MARKET':

                        for strategy in self.strategy_instances:
                            strategy.on_market_event(event)  # MarketEvent, 喂给策略，生成信号

                        self.portfolio.on_market_event(event)  # MarketEvent, 喂给portfolio, 调整position_sizing && 调整限价单价格
                        self.execution_handler.on_market_event(event)  # 如果需要通过order_book精确的估计能否成交 ...

                    elif event.type == 'SIGNAL':
                        self.portfolio.on_signal_event(event)

                    elif event.type == 'ORDER':
                        self.execution_handler.on_order_event(event)

                    elif event.type == 'FILL':
                        self.portfolio.on_fill_event(event)
