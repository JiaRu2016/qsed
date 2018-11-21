import requests
import datetime
import json
import time
from .APIKeyAuthWithExpires import APIKeyAuthWithExpires
from .utils import check_bar_type
from qsUtils import generate_logger


class bitmexREST(object):
    """bitmex REST connection"""
    
    def __init__(self, apiKey, apiSecret, isTestNet=True, loglevel='debug', logfile=None):
        
        self.logger = generate_logger('bitmexREST', loglevel, logfile)
        
        self.apiKey = apiKey
        self.apiSecret = apiSecret
        self.isTestNet = isTestNet
        
        self.base_url = 'https://testnet.bitmex.com/api/v1/' if self.isTestNet else 'https://www.bitmex.com/api/v1/'
        self.clientOrderID = 0
        
    def _send_http_request(self, verb, path, postdict=None, query=None):
        """send HTTP request"""
        url = self.base_url + path
        if self.apiKey is not None and self.apiSecret is not None:
            auth = APIKeyAuthWithExpires(self.apiKey, self.apiSecret)
        else:
            auth = None
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

    def query_history_bars(self, symbol, startTime, endTime, bar_type):
        """查询历史K线"""
        check_bar_type(bar_type)

        verb = 'GET'
        endpoint = 'trade/bucketed'
        params = {
            'symbol': symbol,
            'startTime': startTime,
            'endTime': endTime,
            'binSize': bar_type,
            'partial': 'false',
        }
        return self._page_query(verb, endpoint, params)

    def query_history_ticks(self, symbol, startTime, endTime):
        """查询历史tick"""

        verb = 'GET'
        endpoint = 'trade'
        params = {
            'symbol': symbol,
            'startTime': startTime,
            'endTime': endTime,
        }
        return self._page_query(verb, endpoint, params)

    def query_history_execution(self, symbol, startTime=None, endTime=None):
        """查询成交历史"""
        verb = 'GET'
        endpoint = 'execution'
        params = {
            'symbol': symbol,
            'columns': None,
                # ["execType", "execID", "orderID", "text", "clOrdID", "account", "timestamp",
                #  "symbol", "side", "lastQty", "lastPx",
                #  "orderQty", "price", "ordType", "ordStatus",
                #  "leavesQty", "cumQty", "avgPx",
                #  "commission", "execComm"],
            'startTime': startTime,
            'endTime': endTime,
        }
        return self._page_query(verb, endpoint, params)

    def query_history_order(self, symbol, startTime=None, endTime=None):
        """查询委托历史"""
        verb = 'GET'
        endpoint = 'order'
        params = {
            'symbol': symbol,
            'columns': None,
            'startTime': startTime,
            'endTime': endTime
        }
        return self._page_query(verb, endpoint, params)

    def query_history_wallet(self, currency='XBt'):
        """查询钱包余额历史"""
        verb = 'GET'
        endpoint = 'user/walletHistory'
        params = {
            'currency': currency,
            'count': 500,
            'start': 0
        }
        return self._page_query(verb, endpoint, params)

    def _page_query(self, verb, endpoint, params, count=500):
        """通用功能：分页查询
        bitmex限制查询每次最多500条，利用params中的 start & count 来分页查询
        """
        # print('Calling _page_query....')
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
                    # print('new page...')
            else:
                self.logger.warning('_page_query() res.ok is not True\nstatus_code:%d\n%s' % (res.status_code, res.content))
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


def test_query_market():
    """查询历史行情测试"""
    import pandas as pd

    # from bitmex.bitmexAccountSettings import bitmexAccountSettings
    # acc = bitmexAccountSettings()
    # acc.from_config_file('bitmex/BITMEX_connect.json', 'account_real_market_data')
    #
    # bm = bitmexREST(apiKey=acc.apiKey, apiSecret=acc.apiSecret, isTestNet=acc.isTestNet)
    bm = bitmexREST(apiKey=None, apiSecret=None, isTestNet=True)

    print("================ query history ticks ===============")
    result = bm.query_history_ticks('XBTUSD', '2018-10-27 00:00:00', '2018-10-27 00:01:00')
    df = pd.DataFrame(result)
    print(df)

    print("================ query history bars ===============")
    result_bar = bm.query_history_bars('XBTUSD', '2018-10-27', None, '1h')
    df_bar = pd.DataFrame(result_bar)
    print(df_bar)

    
if __name__ == '__main__':
    # test_orders()
    # test_query_execution()
    test_query_market()
