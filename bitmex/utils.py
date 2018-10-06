import logging


def generate_logger(loggername='defaultLogger', loglevel='debug', logfile=None):
    """generate logger"""

    logger = logging.getLogger(loggername)
    
    # level
    logLevelDict = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warn": logging.WARN,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    level = logLevelDict.get(loglevel, logging.DEBUG)
    logger.setLevel(level)
    
    # formatter   # TODO: color
    formatter = logging.Formatter('[%(asctime)s %(name)s %(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # consoleHandler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # fileHandler
    if logfile is not None:
        fh = logging.FileHandler(logfile)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    
    return logger
    
    
def calculate_td_ts(x, bar_type='1m'):
    """"2018-09-29T06:00:17.271Z -> 20180929, 617"""
    # x = '2018-09-29T06:17:34.271Z'
    # bar_type = '4h'
    
    td, sec = x.split('T')
    td = int(td.replace('-', ''))
    
    n, what = int(bar_type[:-1]), bar_type[-1]    
    h,m,s = sec[:8].split(':')
    if what == 'h':
        ts = '%02d' % (int(h)// n * n)
    elif what == 'm':
        ts = h + '%02d' % (int(m) // n * n)
    elif what == 's':
        ts = h + m + '%02d' % (int(s) // n * n)
    else:
        raise ValueError('bar_type pattern should be "\\d[h|m|s]"')
        
    return td,int(ts)