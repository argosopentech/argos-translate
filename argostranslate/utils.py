import logging

from PyQt5.QtCore import *

from argostranslate import settings

logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)


def info(*argv):
    logging.debug(str(argv))


def error(*argv):
    logging.error(str(argv))


class WorkerThread(QThread):
    """Runs a bound function on a thread"""

    def __init__(self, bound_worker_function):
        """Args:
        bound_worker_function (functools.partial)
        """
        super().__init__()
        self.bound_worker_function = bound_worker_function
        self.finished.connect(self.deleteLater)

    def run(self):
        self.bound_worker_function()
