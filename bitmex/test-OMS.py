from OMS import bitmexTargetPositionOMS
from bitmexWSMarket import bitmexWSMarket

import threading
import numpy as np
import queue
import time
import json

############### global ########################################################

event_q = queue.Queue()  # 事件队列
symbol = 'XBTUSD'  # symbol

# apiKey, apiSecret
with open('accounts.json') as f:
    acc = json.load(f)

apiKey = acc[0]['apiKey']
apiSecret = acc[0]['apiSecret']


############################ pushing target_position ############################

def generate_random_target_positon():
    """随机生成target_position的函数"""
    
    global event_q
    global symbol
    
    symbols = (symbol,)  #('XBTUSD', 'ETHUSD')
    n_symbols = len(symbols)
    
    while True:
        pos = np.random.normal(0, 5, n_symbols).astype(int)
        e = {
            'etype': 'TARGET_POSITION_EVENT',
            'data': {s:int(p) for s,p in zip(symbols, pos)}   # NOTE: np.int64 is not json serilizable
        }
        event_q.put(e)
        time.sleep(15)


# 开一个线程，专门生成 target_position event
target_position_td = threading.Thread(target=generate_random_target_positon, args=())
target_position_td.start()


############################ OMS ############################

# market  (to be part of DataHandler)
bm_ws_market = bitmexWSMarket()
bm_ws_market.addEventQueue(event_q)
bm_ws_market.connect()
bm_ws_market.subscribe(symbol)   # 目前只实现了单品种
bm_ws_market.wait_for_lastprice()  


oms = bitmexTargetPositionOMS(bm_ws_market, event_q, apiKey, apiSecret, (symbol,))

# 持续交易
oms.run()

# # 一次性测试 trade_to_target()
# oms.set_target_position('XBTUSD', 7)
# oms.trade_to_target('XBTUSD')