import requests
import datetime
import json
import time
from APIKeyAuthWithExpires import APIKeyAuthWithExpires
from utils import generate_logger


class bitmexREST(object):
    """bitmex REST connection"""
    
    def __init__(self, apiKey, apiSecret, is_test=True, loglevel='debug', logfile=None):
        
        self.logger = generate_logger('bitmexREST', loglevel, logfile)
        
        self.apiKey = apiKey
        self.apiSecret = apiSecret
        self.is_test = is_test
        
        self.base_url = 'https://testnet.bitmex.com/api/v1/' if is_test else ''   # no real trading now
        self.clientOrderID = 0
        
    def _send_http_request(self, verb, path, postdict=None, query=None):
        """send HTTP request"""
        url = self.base_url + path
        auth = APIKeyAuthWithExpires(self.apiKey, self.apiSecret)
        return requests.request(verb, url, json=postdict, params=query, auth=auth)
    
    def place_order(self, symbol, side, qty, limit_price, text=''):
        """place order"""
        
        path = 'order'
        post_dict = {
            'symbol': symbol,
            'side': side,   # 'Buy' or 'Sell'
            'orderQty': qty,
            'price': limit_price,
            'ordType': 'Limit' if limit_price else 'Market',
            'clOrdID': int(time.time() * 1e6),   # TODO: fix bug Duplicate clOrdID
            'text': self._add_ts(text)
        }
        self.clientOrderID += 1
        self.logger.info('Placing Order... post_dict is %s' % post_dict)
        return self._send_http_request('POST', path, post_dict)
        
    def cancel_order(self, orderID=None, clOrdID=None, text=''):
        path = 'order'
        post_dict = {
            'orderID': orderID,
            'clOrdID': clOrdID,
            'text': self._add_ts(text)
        }
        self.logger.info('Canceling Order... orderID is %s' % orderID)
        return self._send_http_request('DELETE', path, postdict=post_dict)
    
    def cancel_all_orders(self, symbol=None, side=None, text=''):
        path = 'order/all'
        post_dict = {
            'symbol': symbol,
            'filter': json.dumps({'side': side})  # side: 'Buy' or 'Sell'
        }
        self.logger.info('Canceling All Orders... symbol=%s, side=%s' % (symbol, side))
        return self._send_http_request('DELETE', path, postdict=post_dict)
        
        
    def get_open_orders(self, symbol=None):
        """Get open orders"""
        
        path = 'order'
        query = {
            'symbol': symbol,
            'filter': json.dumps({"ordStatus": "New"})
        }
        return self._send_http_request('GET', path, query=query)
    
    def get_positions(self, symbol=None):
        """Get positions"""
        
        path = 'position'
        query = {}
        if symbol:
            query.update({'filter': json.dumps({'symbol': symbol})})
        return self._send_http_request('GET', path, query=query)
    
    @staticmethod
    def _add_ts(text):
        return '[API][%s] %s' % (str(datetime.datetime.now()), text)
    
    
if __name__ == '__main__':
    
    import json

    
    with open('accounts.json') as f:
        acc = json.load(f)

    apiKey = acc[0]['apiKey']
    apiSecret = acc[0]['apiSecret']
    bm = bitmexREST(apiKey, apiSecret)

    res = bm.get_positions()
    if res.ok:
        print(res.json()[0]['symbol'], res.json()[0]['currentQty'])

    res = res = bm.get_open_orders()
    if res.ok:
        print(res.json())

    res = bm.place_order(symbol='XBTUSD', side='Sell', qty=100, limit_price=None)
    if res.ok:
        print(res.json())

    res = bm.place_order(symbol='XBTUSD', side='Buy', qty=120, limit_price=6365.0)
    if res.ok:
        print(res.json())