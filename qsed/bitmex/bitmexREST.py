import requests
import datetime
import json
import time
from .APIKeyAuthWithExpires import APIKeyAuthWithExpires
from qsUtils import generate_logger


class bitmexREST(object):
    """bitmex REST connection"""
    
    def __init__(self, apiKey, apiSecret, isTestNet=True, loglevel='debug', logfile=None):
        
        self.logger = generate_logger('bitmexREST', loglevel, logfile)
        
        self.apiKey = apiKey
        self.apiSecret = apiSecret
        self.isTestNet = isTestNet
        
        self.base_url = 'https://testnet.bitmex.com/api/v1/' if self.isTestNet else 'https://www.bitmex.com/api/v1'
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
            'clOrdID': int(time.time() * 1e6),
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

    def query_history_bars(self):
        """查询历史K线"""
        pass

    def query_history_ticks(self):
        """查询历史tick"""
        pass

    def query_history_execution(self, symbol, startTime=None, endTime=None):
        """查询成交历史"""
        verb = 'GET'
        endpoint = 'execution'
        params = {
            'symbol': symbol,
            'columns': ["execType", "execID", "orderID", "text", "clOrdID", "account", "timestamp",
                        "symbol", "side", "lastQty", "lastPx",
                        "orderQty", "price", "ordType", "ordStatus",
                        "leavesQty", "cumQty", "avgPx",
                        "commission", "execComm"],
            'startTime': startTime,
            'endTime': endTime,
        }
        return self._page_query(verb, endpoint, params)

    def query_history_order(self):
        """查询委托历史"""
        pass

    def _page_query(self, verb, endpoint, params, count=500):
        """通用功能：分页查询
        bitmex限制查询每次最多500条，利用params中的 start & count 来分页查询
        """
        result = []
        params['count'] = count
        params['start'] = 0
        while True:
            res = self._send_http_request(verb, endpoint, params)
            if res.ok:
                data = res.json()
                result.extend(data)
                if len(data) < count:
                    break
                else:
                    params['start'] += count
        return result


def test_orders():
    """下单接口测试"""

    import json
    from bitmex.bitmexAccountSettings import bitmexAccountSettings

    acc = bitmexAccountSettings()
    acc.from_config_file('bitmex/BITMEX_connect.json')

    bm = bitmexREST(acc.apiKey, acc.apiSecret, acc.isTestNet)

    res = bm.get_positions()
    if res.ok:
        print(res.json()[0]['symbol'], res.json()[0]['currentQty'])

    res = bm.get_open_orders()
    if res.ok:
        print(res.json())

    res = bm.place_order(symbol='XBTUSD', side='Sell', qty=100, limit_price=None)
    if res.ok:
        print(res.json())

    res = bm.place_order(symbol='XBTUSD', side='Buy', qty=120, limit_price=6365.0)
    if res.ok:
        print(res.json())

def test_query_execution():
    """查询交易相关数据测试"""

    import json
    import pandas as pd

    from bitmex.bitmexAccountSettings import bitmexAccountSettings

    acc = bitmexAccountSettings()
    acc.from_config_file('bitmex/BITMEX_connect.json')

    bm = bitmexREST(acc.apiKey, acc.apiSecret, acc.isTestNet)

    result = bm.query_history_execution('XBTUSD', '2018-10-27 00:00:00', '2018-10-27 24:00:00')
    df = pd.DataFrame(result)
    print(df)

    
if __name__ == '__main__':
    # test_orders()
    test_query_execution()
