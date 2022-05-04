import logging

from argostranslate import settings

logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)


def info(*argv):
    """Info level log"""
    logging.debug(str(argv))


def error(*argv):
    """Error level log"""
    logging.error(str(argv))
