import queue
import threading


class Event:
    """事件对象"""

    def __init__(self, type_=None):
        self.type_ = type_
        self.dict_ = {}

    def __repr__(self):
        return '<EventObject> type_=%s, dict_=%s' % (self.type_, self.dict_)


class eventEngine(object):
    """事件驱动引擎（通用）"""

    def __init__(self):
        self.__queue = queue.Queue()    # 事件队列
        self.__handlers = {}            # 事件处理函数映射
        self.__general_handlers = []    # 通用事件处理函数
        self.__run_thread = None        # 事件处理线程
        self.__active = False           # 引擎开关

        self.register_general_handler(self.__print_event)

    def __print_event(self, event):
        assert isinstance(event, Event)
        print('✅ ✅ ✅  Event ✅ ✅ ✅   type_=%s, dict_=%s' % (event.type_, event.dict_))

    def start(self):
        """启动引擎"""
        self.__active = True
        self.__run_thread = threading.Thread(target=self.__run)
        self.__run_thread.start()

    def stop(self):
        """停止引擎"""
        self.__active = False
        self.__run_thread.join()

    def __run(self):
        """从队列中不断取出事件并处理"""
        while self.__active:
            try:
                event = self.__queue.get(timeout=5)
            except queue.Empty:
                print('❎  eventEngine ❎  5 seconds no event')
            else:
                self.__process(event)

    def __process(self, event):
        """根据事件类型，分发給不同的handlers处理"""
        assert isinstance(event, Event)
        event_type = event.type_
        if event_type in self.__handlers:
            for func in self.__handlers[event_type]:
                func(event)
                #func()   # func(event)  TODO: 仍为带参数的，但注册的on_tick事件handlers为strategy分发器，分发器再次调用每个实际策略的的on_tick()
        if self.__general_handlers:
            for func in self.__general_handlers:
                func(event)

    def register(self, event_type, func):
        """注册事件处理函数"""
        assert callable(func), 'arg func must be callable. func is %s' % func
        if event_type not in self.__handlers:
            self.__handlers[event_type] = list()
        self.__handlers[event_type].append(func)

    def unregister(self, event_type, func):
        """注销事件处理函数"""
        if event_type in self.__handlers:
            if func in self.__handlers[event_type]:
                self.__handlers[event_type].remove(func)
            else:
                print('func %s is not in self.__handlers[event_type] list' % func)
        else:
            print('event_type %s is not in self.__handlers' % event_type)

    def register_general_handler(self, func):
        self.__general_handlers.append(func)

    def unregister_general_handler(self, func):
        if func in self.__general_handlers:
            self.__general_handlers.remove(func)

    def put(self, event):
        """向队列中放入事件"""
        assert isinstance(event, Event)
        self.__queue.put(event)


def test():
    import random
    import time
    from .eventType import EVENT_MARKET, EVENT_TARGET_POSITION

    def printA(event):
        print('************** %s' % event)

    def printB(event):
        print('============== %s' % event)

    ee = eventEngine()
    ee.register(EVENT_MARKET, printA)
    ee.register(EVENT_TARGET_POSITION, printB)
    ee.start()

    while True:
        try:
            t = random.sample([EVENT_TARGET_POSITION, EVENT_MARKET], k=1)[0]
            event = Event(type_=t)
            ee.put(event)
            time.sleep(1)
        except KeyboardInterrupt:
            ee.stop()
            break


if __name__ == '__main__':
    test()