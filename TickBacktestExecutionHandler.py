from .execution import ExecutionHandler


class TickBacktestExecutionHandler(ExecutionHandler):
    """
    Tick级回测 模拟成交器

    模拟成交机制：
    - 接收到OrderEvent的下一个Tick尝试执行order
    - if 市价单: walk through the order book
    - elif 限价单: 每档价位不超过挂单量的1/2，如果超过，认为不能全部成交，发送部分成交的FillEvent, 剩余的量等待下一个Tick再继续成交
    - 暂时不考虑订单排队问题
    """

    def __init__(self, event_queue, data_handler):
        self.event_queue = event_queue
        self.data_handler = data_handler

    def on_order_event(self, event):
        pass

    def on_market_event(self, event):
        pass
