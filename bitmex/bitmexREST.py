import requests
import datetime
import json
from APIKeyAuthWithExpires import APIKeyAuthWithExpires

class bitmexREST(object):
    """bitmex REST connection"""
    
    def __init__(self, apiKey, apiSecret, is_test=True):
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
            'clOrdID': self.clientOrderID,
            'text': self._add_ts(text)
        }
        self.clientOrderID += 1
        return self._send_http_request('POST', path, post_dict)
        
    def cancel_order(self, orderID=None, clOrdID=None, text=''):
        path = 'order'
        post_dict = {
            'orderID': orderID,
            'clOrdID': clOrdID,
            'text': self._add_ts(text)
        }
        return self._send_http_request('DELETE', path, postdict=post_dict)
    
    def cancel_all_orders(self, symbol=None, side=None, text=''):
        path = 'order/all'
        post_dict = {
            'symbol': symbol,
            'filter': json.dumps({'side': side})  # side: 'Buy' or 'Sell'
        }
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