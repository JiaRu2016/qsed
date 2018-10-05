from bitmexWS import bitmexWS
from bitmexREST import bitmexREST
from utils import generate_logger
import time

#from qsEvent import MarketEvent
#from qsObject import Bar
#from utils import calculate_ts

class MarketEvent(object):
    def __init__(self, data):
        self.etype='MARKET'
        self.data = data
       
    
class Bar(object):
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    
    def __repr__(self):
        return self.__dict__.__repr__()
    
    
def calculate_ts(timestamp, bar_type='1m'):
    """bitmex-timestamp to ts. eg 2018-09-29T06:00:17.271Z -> 20180929060017"""
    return timestamp[:16].replace('T', ' ')  # TODO: now only allow '1m'

class bitmexWSMarket(bitmexWS):
    """bitmexWS subscribing market data (single symbol)"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = generate_logger('bitmexWS_Market')
    
    def addEventQueue(self, q):
        self.eventQueue = q

    def subscribe(self, symbol='XBTUSD', bar_type='1m', subscribe_tick=True):
        self.symbol = symbol
        self.bar_type = bar_type
        self.subscribe_tick = subscribe_tick
        self.subscribe_topic('trade:%s' % symbol)  # TODO: subscribe more topic, such as order book
        self._got_partial = False
        self.last_price = None
        
    def wait_for_lastprice(self):
        while self.last_price is None:
            self.logger.debug('waiting for lastprice ...')
            time.sleep(1)
        
    def onData(self, msg):
        if self._got_partial:
            self._handle_data(msg['data'])   # msg['data'] is a list of dict
        else:
            if msg['action'] == 'partial':
                self._got_partial = True
                self._handle_init_data(msg['data'])
                self.logger.debug('Got partial.')
            elif msg['action'] == 'insert':
                self.logger.debug('drop data before partial')
    
    def _handle_init_data(self, data):
        tick_d = data[-1]
        ts = calculate_ts(tick_d['timestamp'], self.bar_type)
        tick_price = tick_d['price']
        self.last_price = tick_price
        init_bar = Bar(open=tick_price, high=tick_price, low=tick_price, ts=ts)
        self.current_bar = init_bar
        self.logger.debug('init_bar: %s' % init_bar)
    
    def _handle_data(self, data):
        # data is list of dict: [{}, {}]
        # eg 'data': [{'symbol': 'XBTUSD', 'tickDirection': 'PlusTick', 'timestamp': '2018-09-29T06:00:17.271Z', 'price': 6484.5, 'trdMatchID': '87bd9b19-6747-c804-3eae-7a84fc7abcf8', 'foreignNotional': 30, 'grossValue': 462630, 'homeNotional': 0.0046263, 'side': 'Buy', 'size': 30}]
        for tick_d in data:
            self._on_tick(tick_d)
    
    def _on_tick(self, tick_d):
        tick_price = tick_d['price']
        
        # 更新last_price
        self.last_tick_price = self.last_price   # move:self.last_price  -> self.last_tick_price
        self.last_price = tick_price   # **current**_tick_price
        
        # bar-generator
        ts = calculate_ts(tick_d['timestamp'], self.bar_type)  # 'timestamp': '2018-09-29T06:00:17.271Z'
        if ts > self.current_bar.ts:
            # bar_close event
            self.current_bar.close = self.last_tick_price            
            self.prev_bar = self.current_bar
            self.current_bar = Bar(open=tick_price, high=tick_price, low=tick_price, ts=ts)
            
            bar_close_event = MarketEvent(data={'type': 'BAR_CLOSE'})
            self.eventQueue.put(bar_close_event)
            self.logger.debug('bar_close event. prev_bar is %s' % self.prev_bar)
            
            
            # bar_open event
            bar_open_event = MarketEvent(data={'type': 'BAR_OPEN'})
            self.eventQueue.put(bar_open_event)
            self.logger.debug('bar_open event. current_bar is %s' % self.current_bar)
        else:
            self.current_bar.high = max(self.current_bar.high, tick_price)
            self.current_bar.low = min(self.current_bar.low, tick_price)
        # tick event    
        if self.subscribe_tick:
            tick_event = MarketEvent(data={'type':'TICK'})
            self.eventQueue.put(tick_event)
            self.logger.debug('tick event: last_price is %s' % tick_d['price'])
        
if __name__ == '__main__':
    import queue
    import time
    
    events = queue.Queue()

    bm_ws_market = bitmexWSMarket()
    bm_ws_market.addEventQueue(events)
    bm_ws_market.connect()
    bm_ws_market.subscribe('XBTUSD', '1m', True)
    time.sleep(60)
    bm_ws_market.exit()
    
    print('===============================================')
    print(bm_ws_market.current_bar)
    print(bm_ws_market.prev_bar)
    print(bm_ws_market.last_price)   # 考虑每一秒切个片，丢到eventQueue，作为marketEvent,不然太频繁了