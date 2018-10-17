from .bitmexWS import bitmexWS
from .bitmexREST import bitmexREST
from qsUtils import generate_logger
import time
from qsDataStructure import Tick, Orderbook


class bitmexWSMarket(bitmexWS):
    """bitmexWS subscribing market data (single symbol)"""
    
    def __init__(self, *args, **kwargs):
        """
        self.symbols:
        {
          'XBTUSD': Snapshot(last_price, bid1, ask1, bid1vol, ask1vol, 
                              last_price_ts, orderbook_ts,
                              last_price_receiveTime, orderbook_receiveTime)
        }
        """
        super().__init__(*args, **kwargs)
        self.logger = generate_logger('bitmexWS_Market')
        self.symbols = {}   
    
    def add_market_data_q(self, q):
        self.market_data_q = q

    def subscribe(self, symbol, trade=True, orderbook=False):
        self.symbols[symbol] = dict(trade=trade, orderbook=orderbook)  # 每订阅一个symbol, 都将其添加进self.symbols字典中
        if trade:
            self.subscribe_topic('trade:%s' % symbol)  # 订阅成交明细
        if orderbook:
            self.subscribe_topic('quote:%s' % symbol)  # 订阅一档委托单簿
        
    def wait_for_data(self, symbols=None, trade=None, orderbook=None):
        """等待第一个数据的到来
        symbols: by default wait for all self.symbols
        trade: if true: 检查last_price是否为None
        orderbook:  if true: 检查bid1&&bid2是否都不为None
        """
        if symbols is None:
            symbols = self.symbols
        if trade is None:
            trade = False
        if orderbook is None:
            orderbook = False
        while True:
            b_trade = not trade or all(self.symbols[s].last_price is not None for s in symbols)
            b_orderbook = not orderbook or all(self.symbols[s].bid1 is not None and self.symbols[s].ask1 is not None for s in symbols)
            if b_trade and b_orderbook:
                return
            self.logger.debug('waiting for data ...')
            time.sleep(1)
        
    def onData(self, msg):   # 不处理partial了
        msg_handler_dict = {
            'quote': self.__process_quote_msg,
            'trade': self.__process_trade_msg,
        }
        tb = msg.get('table')
        if tb in msg_handler_dict:
            func = msg_handler_dict[tb]
            func(msg)
    
    def __process_quote_msg(self, msg):
        """处理quote订阅：
        组装 Orderbook()
        丢进 market_data_q
        """
        quote_s = msg['data']
        for quote in quote_s:
            ob = Orderbook(symbol=quote['symbol'], 
                           bid1=quote['bidPrice'], bid1vol=quote['bidSize'], 
                           ask1=quote['askPrice'], ask1vol=quote['askSize'], 
                           timestamp = quote['timestamp'])
            self.market_data_q.put(ob)
    
    def __process_trade_msg(self, msg):
        """处理trade订阅：
        组装 Tick()
        丢进 market_data_q
        """
        tick_s = msg['data']
        for tick in tick_s:
            tk = Tick(symbol=tick['symbol'],
                      price=tick['price'],
                      volume=tick['size'],
                      direction=tick['side'],
                      timestamp = tick['timestamp'])
            self.market_data_q.put(tk)
    
 
        
if __name__ == '__main__':
    
    print('------------------------ 加载全局设置 -----------------------------')
    
    from GlobalSettings import GlobalSettings
    g = GlobalSettings()
    g.from_config_file('global_settings.json')
    print(g.__dict__)
    
    print('------------------------ test:bitmexWSMarket2 -----------------------------')
    
    import queue
    import time
    
    market_data_q = queue.Queue()
    
    bm_ws_market = bitmexWSMarket2(apiKey=None, apiSecret=None, 
                                   is_test=g.is_test, loglevel=g.loglevel, logfile=g.logfile)
    bm_ws_market.connect()
    bm_ws_market.add_market_data_q(market_data_q)
    for s in g.symbols:
        bm_ws_market.subscribe(s, trade=True, orderbook=True)
    bm_ws_market.wait_for_data()

    
    print('===============================================')
    while True:
        try:
            a = market_data_q.get(timeout=10)
        except queue.Empty:
            print('warning: no data in 10 sec')
        else:
            if isinstance(a, Tick):
                print('💛 💛 💛 💛 💛   Tick  💛 💛 💛 💛 💛\n %s' % a)
            elif isinstance(a, Orderbook):
                print('✡️ ✡️ ✡️ ✡️ ✡️   Quote  ✡️ ✡️ ✡️ ✡️ ✡️\n %s' % a)