import requests


class SinaLiveDataHandler(object):
    """
    新浪财经实时行情
    http://hq.sinajs.cn/list=<symbol>  symbol must be uppercase

    eg.
    http://hq.sinajs.cn/list=NI1809
    返回字符串:
    var hq_str_NI1809="沪镍1809,145955,109350.00,114800.00,109040.00,109370.00,114000.00,114030.00,114000.00,111930.00,110030.00,52,1,341116,1163434,沪,沪镍,2018-07-12,1,114800.000,108100.000,117920.000,108100.000,118440.000,108100.000,119150.000,102380.000,2620.820";
    对照网页 http://finance.sina.com.cn/futures/quotes/NI1809.shtml，猜测出各个字段的含义：

    """

    def __init__(self):
        pass

    def update(self):
        pass

    def get_latest_bars(self, symbol, n=1):
        pass

    def get_live_tick_by_instrument_id(self, instrument_id):
        """
        获取实时tick行情

        :param instrument_id:
        :return: TickObject
        """
        url = 'http://hq.sinajs.cn/list=%s' % instrument_id.upper()
        res = requests.get(url)
        if res.ok:
            message_string = res.text.split('"')[1]
            vals = message_string.split(',')
            if len(vals) >= 18:
                vals = vals[0:18]
                keys = ['instrument_name', 'update_time', 'day_open', 'highest_price', 'lowest_price', 'day_open_price',
                        'last_price', 'ask1', 'bid1', 'settlement_price', 'prev_settlement_price', 'bid1_q', 'ask1_q',
                        'open_interest', 'volume', 'exchange_name', 'product_name', 'trading_date']
                tick_data = {k: v for k, v in zip(keys, vals)}   # TODO: Tick Object
                return tick_data
            else:
                return None
        else:
            return None


if __name__ == '__main__':

    import time

    data = SinaLiveDataHandler()

    symbol = 'sc1901'   # 测试，用活跃合约

    for _ in range(30):
        tick_data_1 = data.get_live_tick_by_instrument_id(symbol)
        print(tick_data_1)
        time.sleep(3)
