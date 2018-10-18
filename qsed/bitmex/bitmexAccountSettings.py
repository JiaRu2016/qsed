import json
from qsObject import AccountSettings


class bitmexAccountSettings(AccountSettings):
    """bitmex账户配置"""
    
    def __init__(self):
        self.account = None
        self.apiKey = None
        self.apiSecret = None
        self.is_test = None
    
    def from_config_file(self, file, which="account_test"):
        """读取配置文件"""
        
        with open(file) as f:
            st = json.load(f)

        self.account = st[which]['userName']
        self.apiKey = st[which]['apiKey']
        self.apiSecret = st[which]['apiSecret']
        self.isTestNet = st[which]['isTestNet']
