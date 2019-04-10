import logging
from logging import handlers
from os import path

LOG_FOLDER = ""
MAX_BYTES = 1000000  # 1M
logger = None


def set_log_level(logger, new_level:int) -> int:
    """ Set the log level, value is forced with in the [1-5] range

    levels correspond to: DEBUG=5,  INFO=4 WARN=3, ERROR=2 and CRITICAL=1
    """
    if new_level < 1:
        new_level = 1
    elif new_level > 5:
        new_level = 5

    if new_level   == 1:
        logger.setLevel(level=logging.CRITICAL)
    elif new_level == 2:
        logger.setLevel(level=logging.ERROR)
    elif new_level == 3:
        logger.setLevel(level=logging.WARNING)
    elif new_level == 4:
        logger.setLevel(level=logging.INFO)
    elif new_level == 5:
        logger.setLevel(level=logging.DEBUG)


    return new_level

def init(logging_level:int=logging.ERROR, log_file:str=None, ) -> None:

    global logger
    logger = logging.getLogger('ehos')

    formatter = logging.Formatter(fmt='%(asctime)s %(name)s.%(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    if log_file is not None:
        handler = handlers.RotatingFileHandler(log_file, mode='a', maxBytes=MAX_BYTES,
                                                   backupCount=5)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setFormatter(formatter)
        logger.addHandler(screen_handler)

    set_log_level(logger, log_level)

    return logger



def init(log_file='cbu.log', logging_level: str = logging.DEBUG) -> None:
    global logger, MAX_BYTES
    logger = logging.getLogger('cbu')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    try:
        logger.setLevel(logging_level)
    except:
        logger.setLevel(logging.DEBUG)


def info(msg: str) -> None:
    if not logger:
        return
    logger.info(msg)


def debug(msg: str) -> None:
    if not logger:
        return
    logger.debug(msg)


def warning(msg: str) -> None:
    if not logger:
        return
    logger.warning(msg)


def error(msg: str) -> None:
    if not logger:
        return
    logger.error(msg)
