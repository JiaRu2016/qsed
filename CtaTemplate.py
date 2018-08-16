from qsObject import Strategy
from qsEvent import SignalEvent
# from ctaUtils import PnlCalculator # TODO


class TargetPosCtaTemplate(Strategy):
    """
    设置目标仓位的CTA策略模板

    参考vnpy ctaTemplate.py  class TargetPosTemplate(ctaTemplate)
    只管发信号，不管具体的下单，下单由portfolio_object的OMS控制
    多个startegy -> 信号池 -> 合成目标仓位 -> OMS控制下单和成交回报处理

    Notes
    ctaEngine 需要实现的功能
    - DataHandler
    - 多策略多参数配置文件 position.json(position sizing), portfolio.json (identifier -> lots), params.json (identifier -> param)
    - Strategies init, onBar, saveSyncData etc.
    - portfolio 多个产品
        + 组合维护
        + OMS 信号池 -> 合成信号 -> 下单 -> 处理成交回报
        + 组合pnl计算 # TODO
    - ExecutionHandler
    """

    # 策略类名称和作者
    strategyClassName = 'CtaTemplate'
    author = 'Jia Ru'

    # 参数列表
    paramsList = []

    # 变量列表
    varList = ['inited', 'trading', 'pos']  # ['closed_pnl', 'position_pnl', 'net_pnl', 'commission']

    def __init__(self, ctaEngine, config):
        """Constructor"""

        # 设置回测引擎
        self.ctaEngine = ctaEngine

        # 设置策略参数
        self.config = config
        self.identifier = config['identifier']

        # 当前仓位
        self.pos = 0

        # 当前状态（一些状态变量，也可以是止损器类实例）
        self.status = {}

        # 交易记录
        self.trade_history = []

        # pnl计算器
        # self.pnl_calculator = PnlCalculator(config['product_info']) # TODO

    # 策略逻辑部分 必须由用户继承实现 -------------------------------------------
    def onInit(self):
        """初始化策略（必须由用户继承实现）"""
        raise NotImplementedError

    def onStart(self):
        """启动策略（必须由用户继承实现）"""
        raise NotImplementedError

    def onStop(self):
        """停止策略（必须由用户继承实现）"""
        raise NotImplementedError

    def onTick(self, tick):
        """收到tick推送（必须由用户继承实现）"""
        raise NotImplementedError

    def onBarOpen(self, bar):
        """收到bar推送（必须由用户继承实现）"""
        raise NotImplementedError

    def onBarClose(self, bar):
        """收到bar推送（必须由用户继承实现）"""
        raise NotImplementedError

    # 发出策略信号 -------------------------------------------

    def setTargetPosition(self, target_pos, price):
        """发出策略状态变化事件"""

        # 计算单个策略的pnl
        # self.pnl_calculator.target(price, target_pos) # TODO

        # 添加交易记录
        self.addTradeHistory(target_pos, price)

        # 更新 self.pos
        self.pos = target_pos

        # 向ctaEngine发出策略状态变化事件
        e = SignalEvent()
        self.ctaEngine.putSignalEvent(e)

    def addTradeHistory(self, target_pos, price):
        """根据目标仓位和现在的仓位，计算差值，添加到交易记录中"""

        trading_day, ts = self.ctaEngine.now()  # 获取当前时间
        side = 'buy' if target_pos - self.pos > 0 else 'sell'
        volume = abs(target_pos - self.pos)
        trade = dict(trading_day=trading_day,
                     ts=ts,
                     prev_position=self.pos,
                     target_pos=target_pos,
                     price=price,
                     side=side,
                     volume=volume)
        self.trade_history.append(trade)

    # 更新状态 ----------------------------------------------
    def addBarOutput(self):
        pass

    def addDayOutput(self):
        pass

    # 取数据 -----------------------------------------------
    def prev(self, what, n=1):
        self.ctaEngine.get_prev_items(what, n)
