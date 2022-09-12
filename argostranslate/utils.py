import logging
import sys

from argostranslate import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

# Print to standard output if in debug mode
if settings.debug:
    std_out_stream_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(std_out_stream_handler)


def info(*argv):
    """Info level log"""
    logger.debug(str(argv))


def error(*argv):
    """Error level log"""
    logger.error(str(argv))
