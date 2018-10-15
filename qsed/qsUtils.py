import logging
import datetime


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


def now():
    return datetime.datetime.now().__format__('%Y-%m-%d %H:%M:%S.%f')
