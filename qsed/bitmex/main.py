# DEPRECATED, use ROOT/main.py

# 主程序
from .bitmexAccountSettings import GlobalSettings
from qsed.bitmexDataHandler import bitmexDataHandler
import queue

# 加载全局设置
g = GlobalSettings()
g.from_config_file('bitmex/global_settings.json')
print('--------------------- global settings --------------------------- \n%s' % g.__dict__)


# 事件队列
event_q = queue.Queue()

# DataHandler
datahandler = bitmexDataHandler(g)
datahandler.add_event_q(event_q)
datahandler.register_bar_event('XBTUSD', '15s')
datahandler.run()

# datahandler.register_bar_event('XBTUSD', '1m')
# for s,bar_type in params.subscription:
#     datahandler.register_bar_event(s, bar_type)


print('=====================主程序轮询事件队列==========================')
while True:
    try:
        a = event_q.get(timeout=10)
    except queue.Empty:
        print('❎  主进程 ❎ Warning: no data in 10 sec')
    else:
        print('✅ ✅ ✅  主进程事件 ✅ ✅ ✅ %s' % a)



# time.sleep(60)
# datahandler.exit()



