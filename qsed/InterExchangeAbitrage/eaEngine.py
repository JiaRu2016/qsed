from api.bitmex import BitmexWebsocketApi
from api.huobi import HuobiDataApi
from qsUtils import now
import datetime
import time
import os


class HuobiDataApiImpl(HuobiDataApi):
    """火币API具体实现

    - onTradeDetail()
    - onMarketDepth()
    """
    def __init__(self):
        super().__init__()
        self.symbol = ''
        self.last_trade = {}
        self.orderbook = {}

    def onTradeDetail(self, data):
        try:
            exchange_pub_time = self.ts2datetime(data['ts'])
            for d in data['tick']['data']:
                self.last_trade = {
                    'receiveTime': now(),
                    'exchangeTime': exchange_pub_time,
                    'price': d['price']
                }
        except Exception as e:
            print('Error ----------------')
            print(e)

    def onMarketDepth(self, data):
        try:
            self.orderbook['exchagnePubTime'] = self.ts2datetime(data['ts'])
            self.orderbook['receiveTime'] = now()

            self.orderbook['bids'] = data['tick']['bids'][:5]
            self.orderbook['asks'] = data['tick']['asks'][:5]

            self.orderbook['bid1'] = self.orderbook['bids'][0][0]
            self.orderbook['ask1'] = self.orderbook['asks'][0][0]

        except Exception as e:
            print('Error ----------------')
            print(e)


    @staticmethod
    def ts2datetime(ts):
        return datetime.datetime.utcfromtimestamp(ts / 1e3).strftime('%Y-%m-%d %H:%M:%S.%f')


class BitmexWebsocketApiImpl(BitmexWebsocketApi):
    """bitMEX Api具体实现

    覆盖onData()函数
    """
    def __init__(self):
        super().__init__()
        self.symbol = ''
        self.last_trade = {}
        self.orderbook = {}

    def onData(self, data):
        if 'table' in data:
            if data['table'] == 'trade':
                for d in data['data']:
                    self.last_trade = {
                        'receiveTime': now(),
                        'exchangeTime': d['timestamp'],
                        'price': d['price']
                    }
            elif data['table'] == 'quote':
                for d in data['data']:
                    self.orderbook['exchangeTime'] = d['timestamp']
                    self.orderbook['receiveTime'] = now()
                    self.orderbook['bid1'] = d['bidPrice']
                    self.orderbook['ask1'] = d['askPrice']



class eaEngine(object):
    """跨交易所套利引擎"""

    def __init__(self, symbol_huobi='btcusdt', symbol_bitmex='XBTUSD'):

        self.symbol_huobi = symbol_huobi
        self.symbol_bitmex = symbol_bitmex

        self.huobi_api_impl = HuobiDataApiImpl()
        self.bitmex_api_impl = BitmexWebsocketApiImpl()

        self.huobi_api_impl.symbol = symbol_huobi
        self.bitmex_api_impl.symbol = symbol_bitmex

    def run(self):
        print('Starting InterExchangeArbitrage Engine ....')

        # 启动火币
        self.huobi_api_impl.connect("wss://api.huobipro.com/ws")
        self.huobi_api_impl.subscribeTradeDetail(self.symbol_huobi)
        self.huobi_api_impl.subscribeMarketDepth('btcusdt')

        # 启动bitmex
        self.bitmex_api_impl.start()
        req = {"op": "subscribe", "args": ['trade:%s' % self.symbol_bitmex]}  # 行情
        req2 = {"op": "subscribe", "args": ['quote:XBTUSD']}  # 十档订单簿
        self.bitmex_api_impl.sendReq(req)
        self.bitmex_api_impl.sendReq(req2)

        # 500ms一个切片，写入文件
        if not os.path.exists('data/'):
            os.mkdir('data/')

        f = open('data/saved_price_diff.csv', 'w')
        line_header = 'snapshotTime, huobiExchangeTime, bitmexExchangeTime, huobiPrice, bitmexPrice, ' \
                      'huobi_bid1, huobi_ask1, bitmex_bid1, bitmex_ask1, ' \
                      'spread_last, spread_bid, spread_ask\n'
        f.write(line_header)
        f.flush()

        self.__wait_for_first_ticks()

        while True:
            time.sleep(0.5)
            line = self.__snapshot()
            f.write(line)
            f.flush()
            print(line)

    def __snapshot(self):
        huobi_price = self.huobi_api_impl.last_trade['price']
        bitmex_price = self.bitmex_api_impl.last_trade['price']

        huobi_bid1 = self.huobi_api_impl.orderbook['bid1']
        huobi_ask1 = self.huobi_api_impl.orderbook['ask1']
        bitmex_bid1 = self.bitmex_api_impl.orderbook['bid1']
        bitmex_ask1 = self.bitmex_api_impl.orderbook['ask1']

        spread_last = huobi_price - bitmex_price
        spread_bid = huobi_bid1 - bitmex_ask1
        spread_ask = huobi_ask1 - bitmex_bid1

        return '%s, %s, %s, %.2f, %.2f, ' \
               '%.2f, %.2f, %.2f, %.2f, ' \
               '%.2f, %.2f, %.2f\n' % (
            now(),
            self.huobi_api_impl.last_trade['exchangeTime'],
            self.bitmex_api_impl.last_trade['exchangeTime'],
            huobi_price,
            bitmex_price,

            huobi_bid1,
            huobi_ask1,
            bitmex_bid1,
            bitmex_ask1,

            spread_last,
            spread_bid,
            spread_ask
        )

    def __wait_for_first_ticks(self):
        huobi_ok, bitmex_ok = False, False
        while True:
            time.sleep(1)
            if self.bitmex_api_impl.last_trade and self.bitmex_api_impl.orderbook:
                bitmex_ok = True
            else:
                print('waiting for first tick of bitmex...')
            if self.huobi_api_impl.last_trade and self.huobi_api_impl.orderbook:
                huobi_ok = True
            else:
                print('waiting for first tick of huobi...')
            if bitmex_ok and huobi_ok:
                return



def test():
    eng = eaEngine()
    eng.run()


if __name__ == '__main__':
    test()

