from .data import DataHandler
from .event import MarketEvent
import os
import pandas as pd


class CSVDataHandler(DataHandler):
    """
    CSVDataHandler
    """

    def __init__(self, file_dir):
        """
        - Parse the csv file, save to self.__data
        - set self.continue_backtest
        - set self.__cursor

        :param file_dir:
        """
        self._parse_csv_files(file_dir)
        self.continue_backtest = True
        self.__cursor = 0

    def set_event_queue(self, event_queue):
        """
        事件队列
        :param event_queue:
        :return:
        """
        self.events = event_queue

    def update(self):
        if self.__cursor == len(self.__data) - 1:
            self.continue_backtest = False
        else:
            self.__cursor += 1
        self.events.put(MarketEvent())

    def get_prev_bars(self, n=1, columns=None):
        """
        interface for accessing to values of **previous** n bars. Select field(s) by columns, all the columns is selected by default

        :param n:
        :param columns:
        :return: pd.Series if columns is scalar, pd.DataFrame if columns is vector
        """
        if columns is None:
            columns = self.__data.columns.values
        return self.__data.loc[(self.__cursor - n):self.__cursor, columns]

    def get_current_bar(self, columns=None):
        """
        interface for accessing to **current** bar. Select field(s) by columns, all the columns is selected by default

        :param columns:
        :return: pd.Series if columns is vector
        """
        if columns is None:
            columns = self.__data.columns.values
        return self.__data.loc[self.__cursor, columns]

    def _parse_csv_files(self, file_dir):
        """
        parse csv files, save to self.__data

        :param file_dir:  ./data/IF.csv
        :return:
        """
        # file_dir = '../data/IF.csv'
        df = pd.read_csv(file_dir)
        df[['trading_day', 'trading_time']] = df['DATETIME'].str.split('\s', expand=True)
        df['symbol'] = os.path.basename(file_dir).strip('.csv')
        df.reset_index(inplace=True, drop=True)
        self.__data = df
