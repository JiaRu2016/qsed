from bitmexWSTrading import bitmexWSTrading
from bitmexREST import bitmexREST
from utils import generate_logger


class bitmexTargetPositionOMS(object):
    """bitmex TargetPosition-Based Order Management System"""
    
    def __init__(self, bm_ws_market, eventQueue, apiKey, apiSecret, symbols):
        
        # 日志
        self.logger = generate_logger('OMS')
        
        # 绑定事件队列， 队列中只有 TARGET_POSITION_EVENT，另开一个线程来push目标仓位
        self.eventQueue = eventQueue
        
        # 目标仓位 {symbol: pos}
        self.target_position = {}
        
        # 标的
        self.symbols = symbols
        
        # websocket-market
        self.bm_ws_market = bm_ws_market   # 外部的，因为DataHandler同时也在用它 or 它就是DataHandler
        
        # websocket-trading
        self.bm_ws_trading = bitmexWSTrading(apiKey, apiSecret)
        self.bm_ws_trading.connect()
        self.bm_ws_trading.subscribe(self.symbols)
        self.bm_ws_trading.wait_for_initial_status()  # 等待的初始信息

        self.actual_position = self.bm_ws_trading.actual_position  # 由websocket接收的信息计算出的实际仓位 `position`
        self.unfilled_qty = self.bm_ws_trading.unfilled_qty  # 由websocket接收的信息计算出的未成交委托  `order`
        
        # rest
        self.bm_rest = bitmexREST(apiKey, apiSecret)
        
    def exit(self):
        self.bm_ws_trading.exit()
        self.bm_ws_market.exit()
    
    def run(self):
        while True:
            try:
                event = self.eventQueue.get(timeout=100)
            except queue.Empty:
                self.logger.warning('eventQueue is empty for 100 seconds !')
            else:
                if isinstance(event, dict) and event['etype'] == 'TARGET_POSITION_EVENT':
                    for sym, pos in event['data'].items():
                        self.set_target_position(sym, pos)  # 设定目标仓位
                        self.logger.info(' 😍 😍 😍 😍 😍  target_posion: %s 😍 😍 😍 😍 😍' % (self.target_position))
                        self.trade_to_target(sym)    # 交易
                else:
                    self.logger.debug('Event: %s' % event.__repr__())
        
    def set_target_position(self, symbol, position):
        self.target_position[symbol] = position      
        
    def trade_to_target(self, symbol):
        if symbol not in self.symbols:
            self.logger.warning('Calling `trade_to_target` but arg `symbol` is not in self.symbols\n' + 
                                'symbol=%s\n' % symbol +
                                'self.symbols=%s' % self.symbols)
            
        target_pos = self.target_position.get(symbol)  # int
        actual_pos = self.actual_position.get(symbol, 0)  # int
        
        if target_pos is None:
            self.logger.warning('Calling `trade_to_target()` but arg `symbol` is not in self.target_position\n' + 
                                'symbol=%s\nself.target_position=%s' % (symbol, self.target_position))
        
        # 这里采用比较暴力的办法：直接cancel_all_orders, 再挂目标仓位与实际仓位差值的单子
        # 有优化的空间，eg. bitmex支持改单；
        if target_pos == actual_pos:
            unfilled_qty = self.unfilled_qty[symbol]  # {'Buy': 1, 'Sell': 1}
            total_unfilled_qty = sum([abs(x) for x in unfilled_qty.values()])
            if total_unfilled_qty == 0:
                self.logger.info('target_pos == actual_pos && unfilled_qty is 0, nothing to do')
            else:
                self.bm_rest.cancel_all_order(symbol)
        else:
            self.bm_rest.cancel_all_orders(symbol)  # 先全撤掉
            # 构造order
            pos_diff = target_pos - actual_pos
            side = 'Buy' if pos_diff > 0 else 'Sell'
            slippage = 0.5 * 5                  # 测试：5个滑点
            drc = 1 if side == 'Buy' else -1
            price = self.bm_ws_market.last_price + drc * slippage
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
                
    def _check_actual_position_with_rest(self):
        """use REST api to query actual_position, check it with self.actual_position. Use a Thread to do this"""
        pass
    
    
