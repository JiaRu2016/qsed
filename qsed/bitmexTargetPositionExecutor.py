from qsObject import TargetPositionExecutor
from event.eventType import EVENT_TARGET_POSITION
from event.eventEngine import Event
from qsDataStructure import Tick, Orderbook

from bitmex.bitmexWSTrading import bitmexWSTrading
from bitmex.bitmexREST import bitmexREST
from bitmexDataHandler import bitmexDataHandler
from bitmex.utils import generate_logger


class bitmexTargetPositionExecutor(TargetPositionExecutor):
    """基于目标仓位的算法交易逻辑

    1. 对手价挂单
    超过1分钟未成交，且盘口价格已经向不利方向变动，则撤单重新挂。
    2. 信号价 + 滑点
    不成交就算了  -> FillEvent
    3. last_price + 滑点
    超过1分钟未成交，且价格朝不利方向变动，根据最新的last_price重新挂
    """

    def __init__(self, g, account_settings):

        # 全局设置
        self.g = g
        self.logger = generate_logger('bitmexTargetPositionExecutor', self.g.loglevel, self.g.logfile)

        # 账户配置
        self.account_settings = account_settings

        # 目标仓位
        self.target_position = {}       # {symbol: pos}

        # 标的
        self.symbols = self.account_settings.symbols     # 订阅哪些标的的持仓信息

        # data_handler
        self.data_handler = None

        # event engine
        self.event_engine = None

        # websocket-trading
        self.bm_ws_trading = bitmexWSTrading(self.account_settings.apiKey, self.account_settings.apiSecret)
        self.bm_ws_trading.connect()
        self.bm_ws_trading.subscribe(self.symbols)
        self.bm_ws_trading.wait_for_initial_status()  # 等待的初始信息

        self.actual_position = self.bm_ws_trading.actual_position  # 由websocket接收的信息计算出的实际仓位 `position`
        self.unfilled_qty = self.bm_ws_trading.unfilled_qty  # 由websocket接收的信息计算出的未成交委托  `order`

        # rest
        self.bm_rest = bitmexREST(self.account_settings.apiKey, self.account_settings.apiSecret)

    def on_target_position_event(self, event):
        # < EventObject > type_ = eTargetPosition, dict_ = {'XBTUSD': 0}
        assert isinstance(event, Event)
        assert event.type_ == EVENT_TARGET_POSITION

        for symbol, pos in event.dict_.items():
            old_pos = self.target_position.get(symbol)
            if pos != old_pos:
                self.__update_target_position(symbol, pos)
                self.__trade_to_target(symbol)

    def on_orderbook_event(self, event):
        """orderbook事件回调函数

        是否有未成交订单？是 -> 是否超过一定时间 且 盘口价格已经向不利方向变动？是 -》 Call __trade_to_target()
        """
        pass

    def on_tick_event(self, event):
        """orderbook事件回调函数

        是否有未成交订单？是 -> 是否超过一定时间 且 last_price已经向不利方向变动？是 -》 Call __trade_to_target()
        """
        pass

    def __update_target_position(self, symbol, pos):
        self.target_position[symbol] = pos

    def __trade_to_target(self, symbol):
        """
        先全撤，重新挂单
        """
        if symbol not in self.symbols:
            self.logger.warning('Calling `trade_to_target` but arg `symbol` is not in self.symbols\n' +
                                'symbol=%s\nself.symbols=%s' % (symbol, self.symbols))
            return

        target_pos = self.target_position.get(symbol, None)  # int
        actual_pos = self.actual_position.get(symbol, 0)  # int

        if target_pos is None:
            self.logger.warning('Calling `trade_to_target()` but arg `symbol` is not in self.target_position\n' +
                                'symbol=%s\nself.target_position=%s' % (symbol, self.target_position))
            return

        # 这里采用比较暴力的办法：直接cancel_all_orders, 再挂目标仓位与实际仓位差值的单子
        # 有优化的空间，eg. bitmex支持改单；

        if target_pos == actual_pos:
            unfilled_qty = self.unfilled_qty[symbol]  # {'Buy': 1, 'Sell': 1}
            total_unfilled_qty = sum([abs(x) for x in unfilled_qty.values()])
            if total_unfilled_qty == 0:
                self.logger.info('target_pos == actual_pos && unfilled_qty is 0, nothing to do')
            else:
                self.bm_rest.cancel_all_orders(symbol)
        else:
            self.bm_rest.cancel_all_orders(symbol)  # 先全撤掉
            # 构造order
            pos_diff = target_pos - actual_pos
            side = 'Buy' if pos_diff > 0 else 'Sell'
            slippage = 0.5 * 5    # TODO: slippage is related to symbol. Symbol info const
            drc = 1 if side == 'Buy' else -1

            # last_price as order-limit-price
            assert isinstance(self.data_handler, bitmexDataHandler)
            current_tick = self.data_handler.get_current_tick(symbol)
            assert isinstance(current_tick, Tick)
            last_price = current_tick.price
            price = last_price + drc * slippage

            # 下单
            try:
                res = self.bm_rest.place_order(symbol=symbol, side=side, qty=abs(pos_diff), limit_price=price)
            except Exception as e:
                print('When placing order, an Error raise:\n %s' % e)
            else:
                if res.ok:
                    self.logger.info('Successfully Place Order:\n%s' % res.json())
                else:
                    self.logger.info('Placeing Order Failed:\n%s' % res.json())