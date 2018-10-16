"""
CTA模块中用到的一些配置、对象（类）等
"""


from qsObject import Strategy
import json
import os


class CtaPortfolioSettings(object):
    """CTA组合配置类"""

    def __init__(self):
        self.portfolio = {}            # {identifier: lots}
        self.symbol_multiplier = {}    # {symbol: multiplier}
        self.strategy_configs = []     # [CtaStrategyConfig(), ...]
        self.symbols = []              # ['XBTUSD', ...]
        self.bar_types = []            # [{symbol: bar_type}, ...]

    def from_config_file(self, file=None):
        if file is None:
            file = os.path.join(os.path.dirname(__file__), 'CTA_config.json')  # 本文件同目录下的名为"CTA_config.json"的文件
        with open(file) as f:
            st = json.load(f)
        self.portfolio = st['portfolio']
        self.symbol_multiplier = st['symbol_multiplier']
        self.strategy_configs = [CtaStrategyConfig(**d) for d in st['strategy_configs']]
        self.symbols = st['symbols']
        self.bar_types = st['bar_types']

    def check(self):
        """检查组合配置
        0. identifier: '%s_%s_%s_%s' % (strategy_name, symbol, bar_type, config_id)
        1. symbols
        2. bar_types
        """
        pass


class CtaStrategyConfig(object):
    """CTA策略参数配置类"""

    def __init__(self, identifier, strategy_name, config_id, symbol, bar_type, para):
        self.identifier = identifier
        self.strategy_name = strategy_name
        self.config_id = config_id
        self.symbol = symbol
        self.bar_type = bar_type
        self.para = para

    def __repr__(self):
        return "<CtaStrategyConfig object, identifier=%s> " % self.identifier


class CtaStrategy(Strategy):
    """CTA策略"""

    def on_init(self):
        pass

    def on_bar_close(self):
        pass

    def on_bar_open(self):
        pass

    def on_tick(self):
        pass


if __name__ == '__main__':
    portfolio_config = CtaPortfolioSettings()
    portfolio_config.from_config_file()
    print(portfolio_config.symbols)
    print(portfolio_config.bar_types)
    print(portfolio_config.portfolio)
    print(portfolio_config.symbol_multiplier)
    print(portfolio_config.strategy_configs)