import requests
import pandas as pd
import math
import datetime
import time


class bitmexDataGetter(object):
    """
    Get bitMEX data, from REST API

    - history bar data
    - history tick data
    """

    count = 500    # 每次500条数据
    page_wait = 1    # 每次取数据间隔为1秒

    def __init__(self, symbol, bar_type, start, end):
        self.symbol = symbol

        self._check_bar_type(bar_type)
        self.bar_type = bar_type

        self._check_start_end(start, end)
        self.start = start
        self.end = end

    @staticmethod
    def _check_bar_type(bar_type):
        if bar_type not in ('1m', '5m', '1h', '1d'):
            raise ValueError('bar_type must be one of [1m,5m,1h,1d]')

    @staticmethod
    def _check_start_end(start, end):
        # start = '2018-01-01'
        # end = '2018-01-03'
        start_date = datetime.datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end, '%Y-%m-%d').date()
        if not end_date >= start_date:
            raise ValueError('end >= start is not True')

    @staticmethod
    def _to_timestamp(year, month, day, hour=0, minute=0, second=0, millsecocnd=0):
        """
        NOT USED
        convet to timestamp string, eg. '2018-07-25T08:00:00.000Z'
        """
        return '%04d-%02d-%02dT%02d:%02d%02d.%03dZ' % (year, month, day, hour, minute, second, millsecocnd)

    def _get_history_bar_data_one_page(self, page):
        url = 'https://www.bitmex.com/api/v1/trade/bucketed'
        params = dict(
            binSize=self.bar_type,
            partial='false',
            symbol=self.symbol,
            count=str(self.count),
            reverse='false',
            start=str(self.count * page),  # page=0, start=0; page=1, start=501; ...
            startTime='%sT00:00:00.000Z' % self.start,
            endTime='%sT23:59:59.999Z' % self.end,
        )
        headers = {'content-type': 'application/json'}

        col_order = ['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover', 'vwap', 'trades',
                     'homeNotional', 'foreignNotional']

        r = requests.get(url=url, params=params, headers=headers)
        if r.ok:
            json_data = r.json()
            df = pd.DataFrame(json_data, columns=col_order)
        else:
            df = pd.DataFrame(columns=col_order)

        return df

    def get_history_bar_data(self):
        """

        :param start: str, eg. "2018-05-17"
        :param end: str. eg. "2018-07-25"
        :param symbol: str, eg. "XBTUSD"
        :param bar_type: str, must be one of [1m,5m,1h,1d]
        :param pages_wait: int, second between each query
        :return:
        """

        txt = 'Getting Data: symbol = %s, %s ~ %s, %s' % (self.symbol, self.start, self.end, self.bar_type)
        print(txt)

        start_date = datetime.datetime.strptime(self.start, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(self.end, '%Y-%m-%d').date()
        n_days = (end_date - start_date).days + 1
        bar_dict = {'1m': 60 * 24, '5m': 12 * 24, '1h': 24, '1d': 1}
        total_count = n_days * bar_dict[self.bar_type]
        pages = int(math.ceil(total_count / self.count))

        print('totoal counts should be: %d, total pages should be: %d' % (total_count, pages))

        resulst_lst = [None for _ in range(pages)]

        for page in range(pages):
            try:
                df = self._get_history_bar_data_one_page(page)
                resulst_lst[page] = df
                print('page %d, %s ~ %s' % (page, df.timestamp.iloc[0], df.timestamp.iloc[-1]))
            except Exception as e:
                print('Error occured in getting page: %s' % e)
            time.sleep(self.page_wait)

        self.data = pd.concat([x for x in resulst_lst if x is not None]).reset_index(drop=True)

    def get_history_tick_data(self):
        pass


if __name__ == '__main__':
    symbol = 'ETHU18'
    bar_type = '5m'
    start = '2018-06-19'
    end = '2018-07-26'

    bm_data = bitmexDataGetter(symbol, bar_type, start, end)
    bm_data.get_history_bar_data()
    print(bm_data.data)

    bm_data.data.to_pickle('data/bitMEX_%s_%s_%s_%s.pkl' % (symbol, bar_type, start, end))