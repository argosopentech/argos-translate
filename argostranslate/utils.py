import logging
import sys
import json

from argostranslate import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

# Print to standard output if in debug mode
if settings.debug:
    std_out_stream_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(std_out_stream_handler)


def info(*argv):
    """Info level log"""
    logger.debug(json.dumps([str(arg) for arg in argv]))


def warning(*argv):
    """Warning level log"""
    logger.debug(json.dumps([str(arg) for arg in argv]))


def error(*argv):
    """Error level log"""
    logger.error(json.dumps([str(arg) for arg in argv]))


def critical(*argv):
    """Critical level log"""
    logger.critical(json.dumps([str(arg) for arg in argv]))
