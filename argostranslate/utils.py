import logging

from argostranslate import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

def info(*argv):
    """Info level log"""
    logger.debug(str(argv))


def error(*argv):
    """Error level log"""
    logger.error(str(argv))
