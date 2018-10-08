import json


class GlobalSettings(object):
    """全局设置"""
    
    def  __init__(self):
        self.account = None
        self.apiKey = None
        self.apiSecret = None
        self.is_test = True   # always True until real trading
        self.loglevel = 'debug'
        self.logfile = 'default-log.log'
        self.symbols = ['XBTUSD']    # todo: from strategies config
    
    def from_config_file(self, file):
        """读取配置文件"""
        
        with open(file) as f:
            st = json.load(f)
            
        self.account = st['account']['userName']
        self.apiKey = st['account']['apiKey']
        self.apiSecret = st['account']['apiSecret']
        self.loglevel = st['log']['logLevel']
        self.logfile = st['log']['logFile']