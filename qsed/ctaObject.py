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
        # 1. identifier format
        for config in self.strategy_configs:
            assert isinstance(config, CtaStrategyConfig)
            b = config.identifier == '%s_%s_%s_%s' % (config.strategy_name, config.symbol, config.bar_type, config.config_id)
            if not b:
                raise ValueError('identifier is not consistent with CtaStrategyConfig content: %s' % config.identifier)

        # 2. portoflio identifier and strategy_configs identifier
        idf_portfolio = list(self.portfolio.keys())
        idf_portfolio.sort()
        idf_strategy = list(config.identifier for config in self.strategy_configs)
        idf_strategy.sort()
        if not idf_strategy == idf_portfolio:
            raise ValueError('identifier in portfolio != identifier in strategy_configs')

        # 3. bar_type
        bar_type_strategy = list({config.symbol:config.bar_type} for config in self.strategy_configs)
        bar_type_ = list(self.bar_types)
        if not all(x in bar_type_strategy for x in bar_type_):
            raise ValueError('x in bar_type not in bar_type_strategy')
        if not all(x in bar_type_ for x in bar_type_strategy):
            raise ValueError('x bar_type_strategy not in bar_type_')

        # 4. symbols
        symbols_strategy = set(config.symbol for config in self.strategy_configs)
        symbols_ = set(self.symbols)
        if not symbols_strategy == symbols_:
            raise ValueError('symbols in strategy_configs != symbols')


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

    def __init__(self, config):
        assert isinstance(config, CtaStrategyConfig)
        self.config = config
        self.identifier = self.config.identifier
        self.symbol = self.config.symbol
        self.bar_type = self.config.bar_type
        self.para = self.config.para
        print('Calling CtaStrategy.__init__() ..........')

    def on_init(self):
        pass

    def on_bar_close(self, evnet):
        pass

    def on_bar_open(self, event):
        pass

    def on_tick(self, event):
        pass

    def on_orderbook(self, event):
        pass


if __name__ == '__main__':
    portfolio_config = CtaPortfolioSettings()
    portfolio_config.from_config_file()
    print(portfolio_config.symbols)
    print(portfolio_config.bar_types)
    print(portfolio_config.portfolio)
    print(portfolio_config.symbol_multiplier)
    print(portfolio_config.strategy_configs)