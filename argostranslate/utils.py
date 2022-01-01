import logging

from argostranslate import settings

logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)


def info(*argv):
    logging.debug(str(argv))


def error(*argv):
    logging.error(str(argv))
