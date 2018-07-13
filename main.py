# 主程序


import queue
import time

from CSVDataHandler import CSVDataHandler
from TurtleStrategy import TurtleStrategy
from NaivePortfolio import NaivePortfolio
from TickBacktestExecutionHandler import TickBacktestExecutionHandler


events = queue.Queue()   # 事件队列

data_handler = CSVDataHandler('data/sample.csv')
strategy = TurtleStrategy(events, data_handler, {})   # TODO: multiple strategies
portfolio = NaivePortfolio(events, data_handler)
execution_handler = TickBacktestExecutionHandler(events, data_handler)


while True:

    time.sleep(1)
    data_handler.update()  # 生成 MarketEvent

    while True:
        try:
            event = events.get(block=False)
        except queue.Empty:
            break
        else:
            # 根据事件的不同类型，调用各自的 handlers 处理事件
            if event.type == 'MARKET':
                strategy.on_market_event(event)    # MarketEvent, 喂给策略，生成信号
                portfolio.on_market_event(event)    # MarketEvent, 喂给portfolio, 调整position_sizing && 调整限价单价格
                execution_handler.on_market_event(event)   # 如果需要通过order_book精确的估计能否成交 ...

            elif event.type == 'SIGNAL':
                portfolio.on_signal_event(event)

            elif event.type == 'ORDER':
                execution_handler.on_order_event(event)

            elif event.type == 'FILL':
                portfolio.on_fill_event(event)








