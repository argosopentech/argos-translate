import json
import logging
import sys

from argostranslate import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if settings.is_debug else logging.INFO)

# Print to standard output if in debug mode
if settings.is_debug:
    std_out_stream_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(std_out_stream_handler)

# Python Logging Levels:
# https://docs.python.org/3/library/logging.html#levels


def debug(*argv):
    """Debug level log"""
    logger.debug(str(argv))


def get_json_string(argv):
    if len(argv) == 1:
        return json.dumps(str(argv[0]))
    return json.dumps([str(arg) for arg in argv])


def debug(*argv):
    """Debug level log"""
    logger.debug(get_json_string(argv))


def info(*argv):
    """Info level log"""
    logger.info(get_json_string(argv))


def warning(*argv):
    """Warning level log"""
    logger.warning(get_json_string(argv))


def error(*argv):
    """Error level log"""
    logger.error(get_json_string(argv))


def critical(*argv):
    """Critical level log"""
    logger.critical(get_json_string(argv))
