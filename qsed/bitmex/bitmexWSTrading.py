from .bitmexWS import bitmexWS
from .bitmexREST import bitmexREST
from qsUtils import generate_logger
import time


class bitmexWSTrading(bitmexWS):
    """bitmex Websockt subscribing topics related to live trading"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = generate_logger('bitmexWS_Trading')

    def subscribe(self, symbols=('XBTUSD', 'ETHUSD')):
        self.symbols = symbols
        
        self.actual_position = {s:0 for s in symbols}                    # {symbol: pos}   str:int
        self.unfilled_qty = {s:{'Buy': 0, 'Sell': 0} for s in symbols}    # {symbol: {'Buy': qty, 'Sell': qty}}
        
        self._got_position_partial = False
        
        s = ','.join(self.symbols)
        # print('~~~~~~~~~~ subscribing %s ' % s)
        self.subscribe_topic('order:%s' % s)
        self.subscribe_topic('position:%s' % s)
        self.subscribe_topic('execution:%s' % s)
        
    def onData(self, msg):
        if msg.get('table') == 'position':
            self._on_position_msg(msg)
        elif msg.get('table') == 'order':
            self.__on_order_msg(msg)
        elif msg.get('table') == 'execution':
            self.__on_execution_msg(msg)
    
    def _on_position_msg(self, msg):
        self.logger.info('Got position msg:')
        #print('========================position==================\n' + msg.__str__())
        
        #global g_msg
        #g_msg = copy.deepcopy(msg)  ###### 将第一个遇到的msg存入全局变量，调试用
        
        if self._got_position_partial and msg['action'] == 'update':

            if msg['data']:
                
                for d in msg['data']:
                    symbol = d.get('symbol')
                    if symbol not in self.symbols:
                        self.logger.warning('Got position subscription of symbol: %s, not in self.symbols' % symbol)
                        continue
                    currentQty = d.get('currentQty')
                    openOrderBuyQty = d.get('openOrderBuyQty', None)
                    openOrderSellQty = d.get('openOrderSellQty', None)
                    
                    old_pos = self.actual_position.get(symbol)
                    old_buy_qty = self.unfilled_qty.get(symbol, {}).get('Buy')
                    old_sell_qty = self.unfilled_qty.get(symbol, {}).get('Sell')
                    
                    if old_pos != currentQty:
                        self.actual_position[symbol] = currentQty   
                        self.logger.info('█████ Position update (actual_position) █████ %s: %s -> %s' % (symbol, old_pos, currentQty))
                    if openOrderBuyQty is not None:
                        self.unfilled_qty[symbol]['Buy'] = openOrderBuyQty
                        self.logger.info('███ Position update (unfilled_qty, Buy) ███ %s: %s -> %s' % (symbol, old_buy_qty, openOrderBuyQty))
                    if openOrderSellQty is not None:
                        self.unfilled_qty[symbol]['Sell'] = openOrderSellQty
                        self.logger.info('███ Position update (unfilled_qty, Sell) ███ %s: %s -> %s' % (symbol, old_sell_qty, openOrderSellQty))
            else:
                self.logger.debug('#### Position update #### is []')
            
        elif msg['action'] == 'partial':
            self._got_position_partial = True
            
            if msg['data']:
                for d in msg['data']:
                    symbol = d.get('symbol')
                    if symbol not in self.symbols:
                        self.logger.warning('Got position subscription of symbol: %s, not in self.symbols' % symbol)
                        continue
                    currentQty = d.get('currentQty')
                    openOrderBuyQty = d.get('openOrderBuyQty', 0)                    
                    openOrderSellQty = d.get('openOrderSellQty', 0)
                    
                    self.actual_position[symbol] = currentQty
                    self.unfilled_qty[symbol]['Buy'] = openOrderBuyQty
                    self.unfilled_qty[symbol]['Sell'] = openOrderSellQty
                    
                    txt = '%s  pos: %s, buy: %s, sell: %s' % (symbol, currentQty, openOrderBuyQty, openOrderSellQty)
                    self.logger.debug('██████████ Position partial ██████████ %s' % txt)
            else:
                self.logger.debug('██████████  Position partial ██████████  is []')
            
        
        
    def __on_order_msg(self, msg):
        self.logger.info('Got order msg')
        #print('========================order==================\n' + msg.__str__())
        
    def __on_execution_msg(self, msg):
        self.logger.info('Got execution msg')
        #print('========================execution==================\n' + msg.__str__())
            
        
    def wait_for_initial_status(self):
        if self._got_position_partial:
            return
        else:
            time.sleep(1)


if __name__ == '__main__':
    
    import json
    import time


    with open('accounts.json') as f:
        acc = json.load(f)

    apiKey = acc[0]['apiKey']
    apiSecret = acc[0]['apiSecret']


    a = bitmexWSTrading(apiKey=apiKey, apiSecret=apiSecret)
    a.connect()
    a.subscribe(symbols=('XBTUSD',))
    a.wait_for_initial_status()

    time.sleep(30)
    a.exit()
    
    print(a.actual_position)
    print(a.unfilled_qty)