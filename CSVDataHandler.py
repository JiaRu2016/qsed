from .data import DataHandler


class CSVDataHandler(DataHandler):
    """
    CSVDataHandler
    """

    def __init__(self, file_dir):
        """
        Parse the csv file, save all historical data into self._complete_data

        :param file_dir:
        """
        pass

    def update(self):
        pass

    def get_latest_bars(self, symbol, n=1):
        pass