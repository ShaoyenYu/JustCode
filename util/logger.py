from logging import Logger, Formatter, StreamHandler
import sys


def init_logger(name):
    logger = Logger(name)

    fmt_str = "%(asctime)s %(name)s %(levelname)s: %(message)s"
    fmt = Formatter(fmt=fmt_str, datefmt="%Y-%m-%d %H:%M:%S")

    handler = StreamHandler(stream=sys.stdout)
    handler.setFormatter(fmt)

    logger.addHandler(handler)
    return logger
