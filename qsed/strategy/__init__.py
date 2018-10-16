"""
载入所有策略类
"""


# 每增加一个策略，都在这里import进来

from .EmaStrategy import EmaStrategy
from .TurtleStrategy import TurtleStrategy


# 常量 STRATEGY_CLASS 记录了 CtaStrategyConfig.config_name 与 策略类 的对应关系
# 同样的，每增加一个策略，都在这个字典中手工增加一条记录

STRATEGY_CLASS = {
    'EmaStrategy': EmaStrategy,
    'TurtleStrategy': TurtleStrategy
}