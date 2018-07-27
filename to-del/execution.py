from abc import ABCMeta, abstractmethod


class ExecutionHandler(object):
    """
    Execution Handler 交易执行器

    - 历史数据回测  自行实现模拟成交机制
    - 实盘交易对接
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def on_order_event(self, event):
        raise NotImplementedError('Must implement on_order_event()')
