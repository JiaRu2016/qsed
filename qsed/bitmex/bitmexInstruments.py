class bitmexInstrument(object):
    """bitmex instruments"""

    def __init__(self, symbol, symbolName, lotSize, tickSize):
        self.symbol = symbol
        self.symbolName = symbolName
        self.lotSize = lotSize      # 合约乘数
        self.tickSize = tickSize    # 最小变动价位  <<-- 目前只有这个有用


instruments = {
    'XBTUSD': bitmexInstrument('XBTUSD', '比特币-美元', 1, 0.5),
    'XBTJPY': bitmexInstrument('XBTJPY', '比特币-日元', 100, 100),
    'ETHUSD': bitmexInstrument('ETHUSD', '以太坊-美元', 1, 0.05),
    'ETHXBT': bitmexInstrument('ETHXBT', '以太坊-比特币', 1, 0.00001),
}

# TODO: bitmex 计价货币、结算货币、报价方向 搞清楚 + 如何建模