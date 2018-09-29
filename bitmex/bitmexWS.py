import websocket
import threading
import json
import time
import logging
from APIKeyAuth import generate_nonce, generate_signature
from utils import generate_logger


class bitmexWS(object):
    """bitMEX WebSocket"""
    
    def __init__(self, apiKey=None, apiSecret=None, is_test=True, loglevel='debug', logfile=None):
        
        self.logger = generate_logger('bitmexWS', loglevel, logfile)
        
        self.apiKey = apiKey
        self.apiSecret = apiSecret
        self.shouldAuth = apiKey is not None and apiSecret is not None
        
        self.is_test = is_test
        self.ws_url = 'wss://testnet.bitmex.com/realtime' if is_test else ''
        
        self.ws = None
        self.wst = None
        self.ping_td = None
        self.connected = False
        
    def connect(self):
        self.__connect()
        self.__wait_for_connected()
        self.__start_ping_thread()
        
    def __wait_for_connected(self):
        while not self.connected:
            time.sleep(0.1)
            
    def __start_ping_thread(self):
        self.ping_td = threading.Thread(target=self.__send_ping_forever)
        self.ping_td.start()
            
    def __send_ping_forever(self):
        while self.connected:
            self.logger.debug('>>> send ping')
            self.ws.send('ping')
            time.sleep(5)
        
    def exit(self):
        self.connected = False
        self.logger.info('Exiting ...')
        if self.ping_td:
            self.ping_td.join()
            self.logger.info('ping thread end.')
        if self.ws:
            self.ws.close()
        self.logger.info('Exit bitmexWS (intended)')
        
    def __connect(self):
        """connect to websocket in a thread"""
        
        self.ws = websocket.WebSocketApp(self.ws_url,
                                         on_message=self.__on_message,
                                         on_close=self.__on_close,
                                         on_open=self.__on_open,
                                         on_error=self.__on_error,
                                         header=self.__get_auth()
                                        )
        self.wst = threading.Thread(target=lambda: self.ws.run_forever())
        self.wst.start()
        self.logger.info('ws thread start')
        
    def __get_auth(self):
        """return auth headers"""
        
        if self.shouldAuth is False:
            return []
        
        nonce = generate_nonce()
        return [
            'api-nonce:' + str(nonce),
            'api-signature:' + generate_signature(self.apiSecret, 'GET', '/realtime', nonce, ''),
            'api-key:' + self.apiKey
        ]
    
    def __send_command(self, command, args=None):
        """send a row command"""
        if args is None:
            args = []
        self.ws.send(json.dumps({'op': command, 'args': args}))
        
    def __on_message(self, ws, message):
        """Handler for parsing WS messages"""
        
        #print("========================== MESSAGE ==========================")
        #print(message)
        
        if message == 'pong':
            return
        
        msg = json.loads(message)
        
        # 1. Welcome info
        if 'info' in msg:
            if msg['info'] == 'Welcome to the BitMEX Realtime API.':
                self.connected = True
                self.logger.info('Successful connected to BitMEX WebSocket API')
                
        # 2. subscription
        elif 'subscribe' in msg:
            if msg['success']:
                self.logger.info('Subscribe to %s' % msg['subscribe'])
            else:
                self.logger.warn('Subscription not success: %s' % msg)
                
        # 3. table
        elif 'table' in msg:
            self.onData(msg)
        else:
            self.logger.warn('Unclassified msg; %s' % msg)
    
    def onData(self, msg):
        print('Calling bitmexWS.onData()')   # expected to be overwrite
        
    def __on_error(self, ws, error):
        self.logger.warning('Calling ws.__on_error()')
        self.logger.error(error)
        
    def __on_close(self, ws):
        self.logger.debug('Calling ws.__on_close()')
        del self.wst
        
    def __on_open(self, ws):
        self.logger.debug('Calling ws.__on_open()')
            
    def subscribe_topic(self, topic):
        # {"op": "subscribe", "args": [<SubscriptionTopic>]}
        self.__send_command('subscribe', [topic])
        
        
if __name__ == '__main__':
    with open('accounts.json') as f:
        acc = json.load(f)

    apiKey = acc[0]['apiKey']
    apiSecret = acc[0]['apiSecret']
    loglevel = 'debug'
    logfile = './test-bitmexWS.log'

    print(apiKey)
    print(apiSecret)
    
    what = 'market'
    if what == 'order':
        #### 订阅交易信息
        bmws = bitmexWS(apiKey=apiKey, apiSecret=apiSecret)
        bmws.connect()
        bmws.subscribe_topic('order')   # manual send orders and make fill events on website
    elif what == 'instrument':
        #### 订阅合约信息 无需Authentication
        bmws = bitmexWS(apiKey=apiKey, apiSecret=apiSecret)
        bmws.connect()
        bmws.subscribe_topic('instrument:XBTUSD')
    elif what == 'market':
        #### 订阅行情 无需Authentication
        bmws = bitmexWS(apiKey=None, apiSecret=None)
        bmws.connect()
        bmws.subscribe_topic('trade:XBTUSD')
    else:
        print('invalid subscribe')
    time.sleep(20)
    bmws.exit()